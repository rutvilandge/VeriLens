from pathlib import Path
import json
import time

import joblib
import pandas as pd

from scipy.sparse import load_npz

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)


# =========================================================
# VeriLens — Logistic Regression Baseline v2
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

FEATURE_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "tfidf"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "classical_ml"
    / "saved"
)

RESULT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# Load Features
# =========================================================

def load_features():

    print("📥 Loading feature matrices...")

    X_train = load_npz(
        FEATURE_DIR / "train_features.npz"
    )

    X_validation = load_npz(
        FEATURE_DIR / "validation_features.npz"
    )

    X_test = load_npz(
        FEATURE_DIR / "test_features.npz"
    )

    y_train = pd.read_csv(
        FEATURE_DIR / "train_labels.csv"
    )["label"].values

    y_validation = pd.read_csv(
        FEATURE_DIR / "validation_labels.csv"
    )["label"].values

    y_test = pd.read_csv(
        FEATURE_DIR / "test_labels.csv"
    )["label"].values

    print(
        f"   Train:      {X_train.shape}"
    )

    print(
        f"   Validation: {X_validation.shape}"
    )

    print(
        f"   Test:       {X_test.shape}"
    )

    return (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    )


# =========================================================
# Evaluate Model
# =========================================================

def evaluate_model(
    model,
    X,
    y,
    split_name,
):

    predictions = model.predict(X)

    accuracy = accuracy_score(
        y,
        predictions,
    )

    (
        macro_precision,
        macro_recall,
        macro_f1,
        _,
    ) = precision_recall_fscore_support(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    (
        weighted_precision,
        weighted_recall,
        weighted_f1,
        _,
    ) = precision_recall_fscore_support(
        y,
        predictions,
        average="weighted",
        zero_division=0,
    )

    matrix = confusion_matrix(
        y,
        predictions,
    )

    report = classification_report(
        y,
        predictions,
        zero_division=0,
    )

    print()
    print(
        f"📊 {split_name.upper()} RESULTS"
    )

    print(
        f"   Accuracy:           {accuracy:.4f}"
    )

    print(
        f"   Macro Precision:    {macro_precision:.4f}"
    )

    print(
        f"   Macro Recall:       {macro_recall:.4f}"
    )

    print(
        f"   Macro F1:           {macro_f1:.4f}"
    )

    print(
        f"   Weighted Precision: {weighted_precision:.4f}"
    )

    print(
        f"   Weighted Recall:    {weighted_recall:.4f}"
    )

    print(
        f"   Weighted F1:        {weighted_f1:.4f}"
    )

    print()
    print("   Confusion Matrix:")

    print(matrix)

    print()
    print("   Classification Report:")

    print(report)

    return {
        "accuracy": float(
            accuracy
        ),
        "macro_precision": float(
            macro_precision
        ),
        "macro_recall": float(
            macro_recall
        ),
        "macro_f1": float(
            macro_f1
        ),
        "weighted_precision": float(
            weighted_precision
        ),
        "weighted_recall": float(
            weighted_recall
        ),
        "weighted_f1": float(
            weighted_f1
        ),
        "confusion_matrix": matrix.tolist(),
        "classification_report": report,
    }


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 70)
    print("🧿 VeriLens — Logistic Regression Baseline v2")
    print("=" * 70)

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = load_features()

    print()
    print("=" * 70)
    print("🤖 TRAINING LOGISTIC REGRESSION")
    print("=" * 70)

    print()
    print("Configuration:")
    print("   Solver:     lbfgs")
    print("   C:          2.0")
    print("   Max iter:   2000")
    print("   Random seed: 42")

    model = LogisticRegression(
        max_iter=2000,
        solver="lbfgs",
        C=2.0,
        random_state=42,
    )

    start_time = time.perf_counter()

    model.fit(
        X_train,
        y_train,
    )

    training_time = (
        time.perf_counter()
        - start_time
    )

    print()
    print(
        f"⏱️ Training time: "
        f"{training_time:.2f} seconds"
    )

    # =====================================================
    # Validation Evaluation
    # =====================================================

    validation_metrics = evaluate_model(
        model,
        X_validation,
        y_validation,
        "validation",
    )

    # =====================================================
    # Test Evaluation
    # =====================================================

    test_metrics = evaluate_model(
        model,
        X_test,
        y_test,
        "test",
    )

    # =====================================================
    # Save Model
    # =====================================================

    model_path = (
        MODEL_DIR
        / "logistic_regression_v2.joblib"
    )

    joblib.dump(
        model,
        model_path,
    )

    print()
    print("💾 Model saved:")
    print(
        f"   {model_path}"
    )

    # =====================================================
    # Save Metrics
    # =====================================================

    results = {
        "experiment": "logistic_regression_v2",

        "model": "Logistic Regression",

        "algorithm": (
            "sklearn.linear_model.LogisticRegression"
        ),

        "configuration": {
            "max_iter": 2000,
            "solver": "lbfgs",
            "C": 2.0,
            "random_state": 42,
        },

        "features": {
            "tfidf_features": 15000,
            "engineered_features": 8,
            "total_features": 15008,
        },

        "dataset": {
            "name": "LIAR2",
            "train_rows": int(
                X_train.shape[0]
            ),
            "validation_rows": int(
                X_validation.shape[0]
            ),
            "test_rows": int(
                X_test.shape[0]
            ),
        },

        "training": {
            "rows": int(
                X_train.shape[0]
            ),
            "features": int(
                X_train.shape[1]
            ),
            "training_time_seconds": round(
                training_time,
                4,
            ),
        },

        "validation": validation_metrics,

        "test": test_metrics,
    }

    results_path = (
        RESULT_DIR
        / "logistic_regression_v2_results.json"
    )

    with results_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
        )

    print()
    print("📊 Metrics saved:")
    print(
        f"   {results_path}"
    )

    print()
    print("=" * 70)
    print("✅ LOGISTIC REGRESSION V2 COMPLETE")
    print("=" * 70)

    print()
    print("Created:")

    print(
        "   • ml/models/classical_ml/saved/"
        "logistic_regression_v2.joblib"
    )

    print(
        "   • ml/evaluation/"
        "logistic_regression_v2_results.json"
    )

    print()
    print(
        "🚀 Next: Compare against Linear SVM."
    )


if __name__ == "__main__":
    main()