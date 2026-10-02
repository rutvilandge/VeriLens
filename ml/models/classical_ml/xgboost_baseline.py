from pathlib import Path
import json
import time

import joblib
import numpy as np
from scipy.sparse import load_npz
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from xgboost import XGBClassifier


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[3]

FEATURE_DIR = ROOT / "data" / "processed" / "tfidf"
MODEL_DIR = ROOT / "ml" / "models" / "classical_ml" / "saved"
EVALUATION_DIR = ROOT / "ml" / "evaluation"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("⚡ XGBOOST BASELINE")
print("=" * 70)

print("\n📦 Loading TF-IDF features...")

X_train_sparse = load_npz(
    FEATURE_DIR / "train_features.npz"
)
X_val_sparse = load_npz(
    FEATURE_DIR / "validation_features.npz"
)
X_test_sparse = load_npz(
    FEATURE_DIR / "test_features.npz"
)

y_train = np.loadtxt(
    FEATURE_DIR / "train_labels.csv",
    delimiter=",",
    skiprows=1,
    dtype=int,
)

y_val = np.loadtxt(
    FEATURE_DIR / "validation_labels.csv",
    delimiter=",",
    skiprows=1,
    dtype=int,
)

y_test = np.loadtxt(
    FEATURE_DIR / "test_labels.csv",
    delimiter=",",
    skiprows=1,
    dtype=int,
)

print(f"   Train:      {X_train_sparse.shape}")
print(f"   Validation: {X_val_sparse.shape}")
print(f"   Test:       {X_test_sparse.shape}")


# ============================================================
# DIMENSIONALITY REDUCTION
# ============================================================
# Same representation strategy used for Random Forest.
#
# TF-IDF → TruncatedSVD → XGBoost
#
# SVD is fitted ONLY on training data.
# ============================================================

N_COMPONENTS = 300

print("\n🔄 Reducing TF-IDF dimensions with TruncatedSVD...")
print(f"   Components: {N_COMPONENTS}")

svd_start = time.time()

svd = TruncatedSVD(
    n_components=N_COMPONENTS,
    random_state=42,
)

X_train = svd.fit_transform(X_train_sparse)
X_val = svd.transform(X_val_sparse)
X_test = svd.transform(X_test_sparse)

svd_time = time.time() - svd_start

explained_variance = float(
    svd.explained_variance_ratio_.sum()
)

print(f"   Train reduced shape: {X_train.shape}")
print(f"   Validation shape:    {X_val.shape}")
print(f"   Test shape:          {X_test.shape}")
print(f"   Explained variance:  {explained_variance:.4f}")
print(f"   SVD time:            {svd_time:.2f} sec")


# ============================================================
# XGBOOST MODEL
# ============================================================

print("\n⚡ Training XGBoost...")

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    num_class=6,
    eval_metric="mlogloss",
    tree_method="hist",
    random_state=42,
    n_jobs=-1,
)

training_start = time.time()

model.fit(
    X_train,
    y_train,
    eval_set=[(X_val, y_val)],
    verbose=False,
)

training_time = time.time() - training_start

print(f"   Training time: {training_time:.2f} sec")


# ============================================================
# PREDICTIONS
# ============================================================

print("\n🔮 Generating predictions...")

val_predictions = model.predict(X_val)
test_predictions = model.predict(X_test)


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(y_true, predictions):
    precision_macro, recall_macro, f1_macro, _ = (
        precision_recall_fscore_support(
            y_true,
            predictions,
            average="macro",
            zero_division=0,
        )
    )

    precision_weighted, recall_weighted, f1_weighted, _ = (
        precision_recall_fscore_support(
            y_true,
            predictions,
            average="weighted",
            zero_division=0,
        )
    )

    return {
        "accuracy": float(
            accuracy_score(y_true, predictions)
        ),
        "macro_precision": float(precision_macro),
        "macro_recall": float(recall_macro),
        "macro_f1": float(f1_macro),
        "weighted_precision": float(
            precision_weighted
        ),
        "weighted_recall": float(
            recall_weighted
        ),
        "weighted_f1": float(
            f1_weighted
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            predictions,
        ).tolist(),
        "classification_report": classification_report(
            y_true,
            predictions,
            zero_division=0,
        ),
    }


# ============================================================
# VALIDATION RESULTS
# ============================================================

validation_metrics = calculate_metrics(
    y_val,
    val_predictions,
)

print("\n" + "=" * 70)
print("📊 VALIDATION RESULTS")
print("=" * 70)

print(
    f"Accuracy:          "
    f"{validation_metrics['accuracy']:.4f}"
)

print(
    f"Macro Precision:   "
    f"{validation_metrics['macro_precision']:.4f}"
)

print(
    f"Macro Recall:      "
    f"{validation_metrics['macro_recall']:.4f}"
)

print(
    f"Macro F1:          "
    f"{validation_metrics['macro_f1']:.4f}"
)

print(
    f"Weighted F1:       "
    f"{validation_metrics['weighted_f1']:.4f}"
)

print("\nConfusion Matrix:")
print(
    np.array(
        validation_metrics["confusion_matrix"]
    )
)

print("\nClassification Report:")
print(
    validation_metrics["classification_report"]
)


# ============================================================
# TEST RESULTS
# ============================================================

test_metrics = calculate_metrics(
    y_test,
    test_predictions,
)

print("\n" + "=" * 70)
print("🧪 TEST RESULTS")
print("=" * 70)

print(
    f"Accuracy:          "
    f"{test_metrics['accuracy']:.4f}"
)

print(
    f"Macro Precision:   "
    f"{test_metrics['macro_precision']:.4f}"
)

print(
    f"Macro Recall:      "
    f"{test_metrics['macro_recall']:.4f}"
)

print(
    f"Macro F1:          "
    f"{test_metrics['macro_f1']:.4f}"
)

print(
    f"Weighted F1:       "
    f"{test_metrics['weighted_f1']:.4f}"
)

print("\nConfusion Matrix:")
print(
    np.array(
        test_metrics["confusion_matrix"]
    )
)


# ============================================================
# SAVE MODEL + SVD
# ============================================================

model_path = (
    MODEL_DIR / "xgboost.joblib"
)

svd_path = (
    MODEL_DIR / "xgboost_svd.joblib"
)

joblib.dump(model, model_path)
joblib.dump(svd, svd_path)


# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    "model": "XGBoost",
    "experiment": "Classical ML baseline",
    "dataset": "LIAR2",
    "feature_type": "TF-IDF + TruncatedSVD",
    "original_features": int(
        X_train_sparse.shape[1]
    ),
    "reduced_features": N_COMPONENTS,
    "svd_explained_variance": explained_variance,
    "svd_time_seconds": svd_time,
    "training_time_seconds": training_time,
    "hyperparameters": {
        "n_estimators": 300,
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "objective": "multi:softprob",
        "num_class": 6,
        "eval_metric": "mlogloss",
        "tree_method": "hist",
        "random_state": 42,
    },
    "validation": validation_metrics,
    "test": test_metrics,
}

results_path = (
    EVALUATION_DIR /
    "xgboost_results.json"
)

with open(
    results_path,
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        results,
        file,
        indent=2,
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("💾 FILES SAVED")
print("=" * 70)

print(f"   • {model_path}")
print(f"   • {svd_path}")
print(f"   • {results_path}")

print("\n" + "=" * 70)
print("✅ XGBOOST COMPLETE")
print("=" * 70)

print("\n🚀 Next: Classical ML model comparison.")