"""Beginner project: predict whether a student is at risk of failing math.

The model uses study habits and support indicators. Earlier period grades
(G1/G2), the final grade itself (G3), and demographic fields are excluded.
This is an educational demonstration, not a tool for making decisions about
real students.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA = PROJECT_DIR / "data" / "student-mat.csv"
DEFAULT_OUTPUT = PROJECT_DIR / "outputs"
RANDOM_SEED = 42
TEST_FRACTION = 0.20
FEATURES = [
    "studytime",
    "failures",
    "schoolsup",
    "famsup",
    "paid",
    "activities",
    "higher",
    "internet",
    "absences",
    "traveltime",
    "freetime",
    "goout",
    "Dalc",
    "Walc",
    "health",
]
CATEGORICAL_FEATURES = [
    "schoolsup",
    "famsup",
    "paid",
    "activities",
    "higher",
    "internet",
]


def load_data(data_path: Path = DEFAULT_DATA) -> pd.DataFrame:
    """Read the included math CSV, or fetch the official UCI archive if absent."""
    if data_path.exists():
        return pd.read_csv(data_path, sep=";")

    url = "https://archive.ics.uci.edu/static/public/320/student+performance.zip"
    with urlopen(url, timeout=30) as response:
        archive_bytes = response.read()
    with ZipFile(BytesIO(archive_bytes)) as outer_zip:
        with ZipFile(outer_zip.open("student.zip")) as dataset_zip:
            csv_bytes = dataset_zip.read("student-mat.csv")
    return pd.read_csv(BytesIO(csv_bytes), sep=";")


def stratified_split(
    y: np.ndarray, test_fraction: float = TEST_FRACTION, seed: int = RANDOM_SEED
) -> tuple[np.ndarray, np.ndarray]:
    """Return stable train/test row indices while preserving both class shares."""
    rng = np.random.default_rng(seed)
    train_indices: list[int] = []
    test_indices: list[int] = []
    for label in np.unique(y):
        indices = np.flatnonzero(y == label)
        rng.shuffle(indices)
        count = max(1, int(round(len(indices) * test_fraction)))
        test_indices.extend(indices[:count].tolist())
        train_indices.extend(indices[count:].tolist())
    rng.shuffle(train_indices)
    rng.shuffle(test_indices)
    return np.asarray(train_indices), np.asarray(test_indices)


def sigmoid(values: np.ndarray) -> np.ndarray:
    """Numerically stable-enough sigmoid for this small teaching example."""
    clipped = np.clip(values, -35, 35)
    return 1.0 / (1.0 + np.exp(-clipped))


def fit_logistic_regression(
    x: np.ndarray,
    y: np.ndarray,
    steps: int = 6000,
    learning_rate: float = 0.08,
    regularization: float = 0.02,
) -> tuple[np.ndarray, float]:
    """Fit an L2-regularized, class-balanced logistic model with gradient descent."""
    weights = np.zeros(x.shape[1], dtype=float)
    bias = 0.0
    counts = np.bincount(y.astype(int), minlength=2).astype(float)
    class_weights = len(y) / (2.0 * np.maximum(counts, 1.0))
    row_weights = class_weights[y.astype(int)]
    row_weights = row_weights / row_weights.mean()

    for _ in range(steps):
        probabilities = sigmoid(x @ weights + bias)
        errors = (probabilities - y) * row_weights
        gradient_weights = (x.T @ errors) / len(y) + regularization * weights
        gradient_bias = errors.mean()
        weights -= learning_rate * gradient_weights
        bias -= learning_rate * gradient_bias
    return weights, float(bias)


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, Any]:
    """Calculate transparent binary metrics where class 1 means at risk/fail."""
    true_positive = int(np.sum((y_true == 1) & (y_pred == 1)))
    true_negative = int(np.sum((y_true == 0) & (y_pred == 0)))
    false_positive = int(np.sum((y_true == 0) & (y_pred == 1)))
    false_negative = int(np.sum((y_true == 1) & (y_pred == 0)))
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    specificity = true_negative / (true_negative + false_positive) if true_negative + false_positive else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (true_positive + true_negative) / len(y_true)
    return {
        "accuracy": accuracy,
        "balanced_accuracy": (recall + specificity) / 2,
        "precision_at_risk": precision,
        "recall_at_risk": recall,
        "f1_at_risk": f1,
        "confusion_matrix": {
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "true_positive": true_positive,
        },
    }


def run_analysis(
    data_path: Path = DEFAULT_DATA, output_dir: Path = DEFAULT_OUTPUT
) -> dict[str, Any]:
    """Train, evaluate, save results, and return a report-ready summary."""
    frame = load_data(Path(data_path))
    missing_columns = sorted(set(FEATURES + ["G3"]) - set(frame.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    y = (frame["G3"].to_numpy(dtype=int) < 10).astype(int)
    x_frame = frame[FEATURES].copy()
    train_rows, test_rows = stratified_split(y)

    # Fit dummy encoding and scaling only on the training split.
    x_encoded = pd.get_dummies(x_frame, columns=CATEGORICAL_FEATURES, dtype=float)
    x_train = x_encoded.iloc[train_rows].astype(float)
    x_test = x_encoded.iloc[test_rows].astype(float).reindex(columns=x_train.columns, fill_value=0.0)
    means = x_train.mean(axis=0)
    scales = x_train.std(axis=0, ddof=0).replace(0, 1.0)
    train_values = ((x_train - means) / scales).to_numpy(dtype=float)
    test_values = ((x_test - means) / scales).to_numpy(dtype=float)
    y_train = y[train_rows]
    y_test = y[test_rows]

    weights, bias = fit_logistic_regression(train_values, y_train)
    model_predictions = (sigmoid(test_values @ weights + bias) >= 0.5).astype(int)
    majority_label = int(np.bincount(y_train, minlength=2).argmax())
    baseline_predictions = np.full_like(y_test, majority_label)

    results: dict[str, Any] = {
        "title": "Student Grade Predictor: Early Support Risk Classification",
        "dataset": "UCI Student Performance (mathematics subject)",
        "records": int(len(frame)),
        "features_used": FEATURES,
        "target_definition": "At risk/fail = final math grade G3 below 10 out of 20",
        "excluded_from_features": ["G1", "G2", "G3", "student demographics"],
        "split": {
            "train_rows": int(len(train_rows)),
            "test_rows": int(len(test_rows)),
            "random_seed": RANDOM_SEED,
            "test_fraction": TEST_FRACTION,
        },
        "class_counts": {
            "at_risk_fail": int(y.sum()),
            "not_at_risk_pass": int(len(y) - y.sum()),
        },
        "baseline_majority_class": "at_risk/fail" if majority_label else "not_at_risk/pass",
        "baseline_metrics": classification_metrics(y_test, baseline_predictions),
        "model": "Class-balanced L2 logistic regression (gradient descent)",
        "model_metrics": classification_metrics(y_test, model_predictions),
        "largest_standardized_coefficients": [
            {"feature": str(x_train.columns[index]), "coefficient": float(weights[index])}
            for index in np.argsort(np.abs(weights))[::-1][:8]
        ],
        "caveat": "Small observational dataset; results do not establish cause or support decisions about individual students.",
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def print_summary(results: dict[str, Any]) -> None:
    """Print a compact, beginner-readable evaluation summary."""
    print(f"Dataset rows: {results['records']}")
    print(f"Class counts: {results['class_counts']}")
    print("\nHoldout metrics (positive class = at risk/fail):")
    for label, key in [("Majority baseline", "baseline_metrics"), ("Logistic regression", "model_metrics")]:
        metrics = results[key]
        print(
            f"{label}: accuracy={metrics['accuracy']:.3f}, "
            f"balanced accuracy={metrics['balanced_accuracy']:.3f}, "
            f"precision={metrics['precision_at_risk']:.3f}, "
            f"recall={metrics['recall_at_risk']:.3f}, "
            f"F1={metrics['f1_at_risk']:.3f}"
        )
    print(f"\nSaved metrics to: {DEFAULT_OUTPUT / 'results.json'}")


if __name__ == "__main__":
    summary = run_analysis()
    print_summary(summary)
