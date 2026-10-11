import json
from pathlib import Path

import joblib


ROOT = Path(__file__).resolve().parent
MODELS_PATH = ROOT / "models" / "prediction_models.joblib"
OUTPUT_PATH = ROOT / "models" / "browser_models.json"
TARGETS = ("CAD", "LAD", "LCX", "RCA")


def main() -> None:
    pipelines = joblib.load(MODELS_PATH)
    missing = set(TARGETS) - set(pipelines)
    if missing:
        raise ValueError(f"Missing prediction pipelines: {sorted(missing)}")

    numeric = None
    categorical = None
    targets = {}
    feature_names = None

    for target in TARGETS:
        pipeline = pipelines[target]
        preprocessor = pipeline.named_steps["preprocess"]
        classifier = pipeline.named_steps["classifier"]

        current_names = preprocessor.get_feature_names_out().tolist()
        if feature_names is None:
            feature_names = current_names
        elif current_names != feature_names:
            raise ValueError(f"{target} has a different preprocessor feature layout.")

        for name, transformer, columns in preprocessor.transformers_:
            if name == "numeric":
                steps = transformer.named_steps
                current = {
                    "columns": list(columns),
                    "medians": steps["imputer"].statistics_.tolist(),
                    "means": steps["scaler"].mean_.tolist(),
                    "scales": steps["scaler"].scale_.tolist(),
                }
                if numeric is None:
                    numeric = current
                elif current != numeric:
                    raise ValueError(f"{target} has a different numeric preprocessor.")
            elif name == "categorical":
                steps = transformer.named_steps
                current = {
                    "columns": list(columns),
                    "imputers": steps["imputer"].statistics_.tolist(),
                    "categories": [
                        categories.tolist()
                        for categories in steps["encoder"].categories_
                    ],
                }
                if categorical is None:
                    categorical = current
                elif current != categorical:
                    raise ValueError(f"{target} has a different categorical preprocessor.")

        targets[target] = {
            "intercept": float(classifier.intercept_[0]),
            "coefficients": classifier.coef_[0].tolist(),
        }

    if numeric is None or categorical is None or feature_names is None:
        raise ValueError("Expected numeric and categorical model features.")

    payload = {
        "numeric": numeric,
        "categorical": categorical,
        "feature_names": feature_names,
        "targets": targets,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Exported browser prediction models to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
