from contextlib import asynccontextmanager
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from scipy import sparse


ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models"
MODELS_PATH = MODEL_DIR / "prediction_models.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
SCHEMA_PATH = MODEL_DIR / "schema.json"
INDEX_PATH = ROOT / "index.html"
HEART3D_DIST = ROOT / "heart3d" / "dist"
ARTIFACTS: dict | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global ARTIFACTS
    required = (MODELS_PATH, METRICS_PATH, SCHEMA_PATH)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(
            "Model artifacts are missing. Run `python train_model.py` first. "
            f"Missing: {', '.join(missing)}"
        )
    ARTIFACTS = {
        "models": joblib.load(MODELS_PATH),
        "metrics": json.loads(METRICS_PATH.read_text(encoding="utf-8")),
        "schema": json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
    }
    yield


app = FastAPI(title="CardioScope educational prototype", lifespan=lifespan)
app.mount("/heart3d", StaticFiles(directory=HEART3D_DIST, html=True), name="heart3d")


class PredictionRequest(BaseModel):
    features: dict[str, str | float | int | None]


@app.get("/")
def home() -> FileResponse:
    return FileResponse(INDEX_PATH)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": ARTIFACTS is not None}


@app.get("/api/features")
def get_features() -> dict:
    if ARTIFACTS is None:
        raise HTTPException(status_code=503, detail="Model artifacts are not loaded.")
    return ARTIFACTS["schema"]


@app.get("/api/metrics")
def get_metrics() -> dict:
    if ARTIFACTS is None:
        raise HTTPException(status_code=503, detail="Model artifacts are not loaded.")
    return ARTIFACTS["metrics"]


@app.post("/api/predict")
def predict(request: PredictionRequest) -> dict:
    if ARTIFACTS is None:
        raise HTTPException(status_code=503, detail="Model artifacts are not loaded.")

    models = ARTIFACTS["models"]
    schema = ARTIFACTS["schema"]
    definitions = {item["name"]: item for item in schema["features"]}
    unknown = set(request.features) - set(definitions)
    if unknown:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown or excluded input fields: {', '.join(sorted(unknown))}",
        )
    if not any(
        value is not None and not (isinstance(value, str) and not value.strip())
        for value in request.features.values()
    ):
        raise HTTPException(
            status_code=422,
            detail="Enter at least one patient measurement before requesting a score.",
        )

    row: dict[str, object] = {}
    for name, definition in definitions.items():
        value = request.features.get(name)
        if value == "":
            value = None
        if value is not None and definition["kind"] == "number":
            try:
                value = float(value)
            except (TypeError, ValueError) as error:
                raise HTTPException(
                    status_code=422,
                    detail=f"{name} must be a number.",
                ) from error
        if (
            value is not None
            and definition["kind"] == "category"
            and str(value) not in definition["options"]
        ):
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported value for {name}: {value}",
            )
        row[name] = value

    frame = pd.DataFrame([row], columns=list(definitions))
    cad_model = models["CAD"]
    probability = float(cad_model.predict_proba(frame)[0, 1])
    transformed = cad_model.named_steps["preprocess"].transform(frame)
    if sparse.issparse(transformed):
        transformed = transformed.toarray()
    transformed_values = np.asarray(transformed[0], dtype=float)
    classifier = cad_model.named_steps["classifier"]
    contributions = transformed_values * classifier.coef_[0]
    names = cad_model.named_steps["preprocess"].get_feature_names_out()
    ranked = np.argsort(np.abs(contributions))[::-1][:8]
    explanation = [
        {
            "feature": str(names[index]).split("__", 1)[-1],
            "contribution": float(contributions[index]),
            "direction": "increases" if contributions[index] >= 0 else "decreases",
        }
        for index in ranked
        if contributions[index] != 0
    ]

    vessels = {}
    for name in ("LAD", "LCX", "RCA"):
        vessel_probability = float(models[name].predict_proba(frame)[0, 1])
        vessels[name] = {
            "available": True,
            "probability": vessel_probability,
            "predicted_status": (
                "Stenotic" if vessel_probability >= 0.5 else "Normal"
            ),
        }
    return {
        "cad": {
            "probability": probability,
            "predicted_status": "CAD" if probability >= 0.5 else "Normal",
        },
        "vessels": vessels,
        "explanation": explanation,
    }
