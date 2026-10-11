import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.base import clone


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "extention of Z-Alizadeh sani dataset.xlsx"
MODEL_DIR = ROOT / "models"
MODELS_PATH = MODEL_DIR / "prediction_models.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
SCHEMA_PATH = MODEL_DIR / "schema.json"
TARGET_COLUMNS = {"CAD": "Cath", "LAD": "LAD", "LCX": "LCX", "RCA": "RCA"}
LEAKAGE_COLUMNS = {"lad", "lcx", "rca", "cath"}


def build_schema(frame: pd.DataFrame) -> dict:
    features = []
    for column in frame.columns:
        if pd.api.types.is_numeric_dtype(frame[column]):
            features.append({"name": column, "kind": "number"})
        else:
            options = sorted(
                str(value) for value in frame[column].dropna().unique()
            )
            features.append(
                {"name": column, "kind": "category", "options": options}
            )
    return {"features": features}


def build_pipeline(features: pd.DataFrame) -> Pipeline:
    categorical = [
        column
        for column in features.columns
        if not pd.api.types.is_numeric_dtype(features[column])
    ]
    numeric = [column for column in features.columns if column not in categorical]

    transformers = []
    if numeric:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric,
            )
        )
    if categorical:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            )
        )

    return Pipeline(
        [
            ("preprocess", ColumnTransformer(transformers=transformers)),
            (
                "classifier",
                LogisticRegression(class_weight="balanced", max_iter=2000),
            ),
        ]
    )


def main() -> None:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Dataset workbook not found: {DATA_PATH}")

    data = pd.read_excel(DATA_PATH, sheet_name="Sheet 1 - Table 1")
    missing_targets = sorted(set(TARGET_COLUMNS.values()) - set(data.columns))
    if missing_targets:
        raise ValueError(f"Required target columns are missing: {missing_targets}")

    features = data.drop(
        columns=[
            column
            for column in data.columns
            if column.strip().casefold() in LEAKAGE_COLUMNS
        ]
    )
    if features.empty:
        raise ValueError("No clinical input features remain after target exclusion.")

    pipelines = {}
    target_metrics = {}
    for name, column in TARGET_COLUMNS.items():
        labels = data[column].astype("string").str.strip().str.casefold()
        positive_label = "cad" if name == "CAD" else "stenotic"
        valid_labels = {"cad", "normal"} if name == "CAD" else {"stenotic", "normal"}
        if labels.isna().any():
            raise ValueError(f"Missing labels found in target column {column!r}.")
        invalid_labels = sorted(set(labels) - valid_labels)
        if invalid_labels:
            raise ValueError(f"Unexpected {column} labels: {invalid_labels}")
        target = labels.eq(positive_label).astype(int)
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=0.2,
            random_state=42,
            stratify=target,
        )
        if y_train.nunique() < 2 or y_test.nunique() < 2:
            raise ValueError(
                f"Both classes must be present in the train and test sets for {column}."
            )
        pipeline = build_pipeline(features)
        evaluation_pipeline = clone(pipeline)
        evaluation_pipeline.fit(x_train, y_train)
        predicted = evaluation_pipeline.predict(x_test)
        probabilities = evaluation_pipeline.predict_proba(x_test)[:, 1]
        pipelines[name] = pipeline.fit(features, target)
        positive_class = "CAD" if name == "CAD" else "Stenotic"
        target_metrics[name] = {
            "target_column": column,
            "train_records": int(len(x_train)),
            "test_records": int(len(x_test)),
            "class_counts": {
                positive_class: int(target.sum()),
                "Normal": int((target == 0).sum()),
            },
            "metrics": {
                "accuracy": float(accuracy_score(y_test, predicted)),
                "precision": float(
                    precision_score(y_test, predicted, zero_division=0)
                ),
                "recall": float(recall_score(y_test, predicted, zero_division=0)),
                "f1": float(f1_score(y_test, predicted, zero_division=0)),
                "roc_auc": float(roc_auc_score(y_test, probabilities)),
            },
        }

    metrics = {
        "records": int(len(data)),
        "split": "Each target: stratified 80/20 holdout, random_state=42",
        "targets": target_metrics,
        "note": (
            "Small single holdout; estimates are educational and not clinical "
            "validation."
        ),
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipelines, MODELS_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    SCHEMA_PATH.write_text(
        json.dumps(build_schema(features), indent=2), encoding="utf-8"
    )

    print(f"Saved CAD and vessel models to {MODELS_PATH}")
    print(f"Saved evaluation metrics to {METRICS_PATH}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
