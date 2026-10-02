from pathlib import Path
import json

import joblib
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler


# ============================================================
# CONFIG
# ============================================================

MODEL_DIR = Path("ml/models/multimodal/saved")
RESULTS_DIR = Path("ml/evaluation/multimodal")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


# ============================================================
# FILES
# ============================================================

TEXT_TRAIN = (
    MODEL_DIR /
    "fakeddit_text_train_embeddings.npy"
)

TEXT_VAL = (
    MODEL_DIR /
    "fakeddit_text_validation_embeddings.npy"
)

TEXT_TEST = (
    MODEL_DIR /
    "fakeddit_text_test_embeddings.npy"
)

IMAGE_TRAIN = (
    MODEL_DIR /
    "fakeddit_image_train_features.npy"
)

IMAGE_VAL = (
    MODEL_DIR /
    "fakeddit_image_validation_features.npy"
)

IMAGE_TEST = (
    MODEL_DIR /
    "fakeddit_image_test_features.npy"
)


# ============================================================
# LOAD LABELS
# ============================================================

DATASET_DIR = Path(
    "ml/datasets/multimodal/fakeddit/processed/valid_subset"
)


def load_labels():

    import pandas as pd

    train = pd.read_csv(
        DATASET_DIR / "train.csv"
    )

    validation = pd.read_csv(
        DATASET_DIR / "validation.csv"
    )

    test = pd.read_csv(
        DATASET_DIR / "test.csv"
    )

    y_train = train["2_way_label"].astype(int).to_numpy()
    y_val = validation["2_way_label"].astype(int).to_numpy()
    y_test = test["2_way_label"].astype(int).to_numpy()

    return y_train, y_val, y_test


# ============================================================
# LOAD FEATURES
# ============================================================

def load_features():

    print("=" * 80)
    print("LOADING SAVED TEXT + IMAGE FEATURES")
    print("=" * 80)

    text_train = np.load(TEXT_TRAIN)
    text_val = np.load(TEXT_VAL)
    text_test = np.load(TEXT_TEST)

    image_train = np.load(IMAGE_TRAIN)
    image_val = np.load(IMAGE_VAL)
    image_test = np.load(IMAGE_TEST)

    print()
    print("Text features:")
    print(f"  Train      : {text_train.shape}")
    print(f"  Validation : {text_val.shape}")
    print(f"  Test       : {text_test.shape}")

    print()
    print("Image features:")
    print(f"  Train      : {image_train.shape}")
    print(f"  Validation : {image_val.shape}")
    print(f"  Test       : {image_test.shape}")

    return (
        text_train,
        text_val,
        text_test,
        image_train,
        image_val,
        image_test,
    )


# ============================================================
# STANDARDIZE EACH MODALITY
# ============================================================

def scale_features(
    text_train,
    text_val,
    text_test,
    image_train,
    image_val,
    image_test,
):

    print()
    print("=" * 80)
    print("SCALING MODALITIES")
    print("=" * 80)

    text_scaler = StandardScaler()

    image_scaler = StandardScaler()

    text_train_scaled = text_scaler.fit_transform(
        text_train
    )

    text_val_scaled = text_scaler.transform(
        text_val
    )

    text_test_scaled = text_scaler.transform(
        text_test
    )

    image_train_scaled = image_scaler.fit_transform(
        image_train
    )

    image_val_scaled = image_scaler.transform(
        image_val
    )

    image_test_scaled = image_scaler.transform(
        image_test
    )

    return (
        text_train_scaled,
        text_val_scaled,
        text_test_scaled,
        image_train_scaled,
        image_val_scaled,
        image_test_scaled,
        text_scaler,
        image_scaler,
    )


# ============================================================
# DIMENSIONALITY CONTROL
# ============================================================

def project_features(
    text_train,
    text_val,
    text_test,
    image_train,
    image_val,
    image_test,
):

    print()
    print("=" * 80)
    print("BUILDING BALANCED MULTIMODAL REPRESENTATION")
    print("=" * 80)

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------
    #
    # DistilBERT already provides a compact 768-dimensional
    # semantic representation.
    #
    # --------------------------------------------------------

    text_projection_dim = min(
        256,
        text_train.shape[1],
    )

    text_train_projected = text_train[
        :, :text_projection_dim
    ]

    text_val_projected = text_val[
        :, :text_projection_dim
    ]

    text_test_projected = text_test[
        :, :text_projection_dim
    ]

    # --------------------------------------------------------
    # Image
    # --------------------------------------------------------
    #
    # HOG features are smaller than raw pixels but can still
    # have many dimensions. Keep a balanced representation.
    #
    # --------------------------------------------------------

    image_projection_dim = min(
        256,
        image_train.shape[1],
    )

    image_train_projected = image_train[
        :, :image_projection_dim
    ]

    image_val_projected = image_val[
        :, :image_projection_dim
    ]

    image_test_projected = image_test[
        :, :image_projection_dim
    ]

    print(
        f"Text projection  : {text_projection_dim}"
    )

    print(
        f"Image projection : {image_projection_dim}"
    )

    return (
        text_train_projected,
        text_val_projected,
        text_test_projected,
        image_train_projected,
        image_val_projected,
        image_test_projected,
    )


# ============================================================
# FUSION
# ============================================================

def fuse(
    text_train,
    text_val,
    text_test,
    image_train,
    image_val,
    image_test,
):

    X_train = np.concatenate(
        [text_train, image_train],
        axis=1,
    )

    X_val = np.concatenate(
        [text_val, image_val],
        axis=1,
    )

    X_test = np.concatenate(
        [text_test, image_test],
        axis=1,
    )

    print()
    print("=" * 80)
    print("MULTIMODAL FUSION")
    print("=" * 80)

    print(
        f"Fused train shape : {X_train.shape}"
    )

    print(
        f"Fused val shape   : {X_val.shape}"
    )

    print(
        f"Fused test shape  : {X_test.shape}"
    )

    return X_train, X_val, X_test


# ============================================================
# TRAIN
# ============================================================

def train_model(X_train, y_train):

    print()
    print("=" * 80)
    print("TRAINING MULTIMODAL CLASSIFIER")
    print("=" * 80)

    model = LogisticRegression(
        C=0.5,
        max_iter=2000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        solver="lbfgs",
    )

    model.fit(
        X_train,
        y_train,
    )

    return model


# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    model,
    X,
    y,
    split_name,
):

    predictions = model.predict(X)

    probabilities = model.predict_proba(X)[:, 1]

    accuracy = accuracy_score(
        y,
        predictions,
    )

    precision = precision_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    recall = recall_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y,
        predictions,
        average="weighted",
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y,
        probabilities,
    )

    cm = confusion_matrix(
        y,
        predictions,
    )

    print()
    print("=" * 80)
    print(f"{split_name.upper()} RESULTS")
    print("=" * 80)

    print(
        f"Accuracy       : {accuracy:.4f}"
    )

    print(
        f"Macro Precision: {precision:.4f}"
    )

    print(
        f"Macro Recall   : {recall:.4f}"
    )

    print(
        f"Macro F1       : {macro_f1:.4f}"
    )

    print(
        f"Weighted F1    : {weighted_f1:.4f}"
    )

    print(
        f"ROC-AUC        : {roc_auc:.4f}"
    )

    print()
    print("Confusion Matrix:")
    print(cm)

    return {
        "accuracy": float(accuracy),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "roc_auc": float(roc_auc),
        "confusion_matrix": cm.tolist(),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("VERILENS PHASE 5 — MULTIMODAL FUSION")
    print("=" * 80)

    # --------------------------------------------------------
    # Load features
    # --------------------------------------------------------

    (
        text_train,
        text_val,
        text_test,
        image_train,
        image_val,
        image_test,
    ) = load_features()

    # --------------------------------------------------------
    # Load labels
    # --------------------------------------------------------

    (
        y_train,
        y_val,
        y_test,
    ) = load_labels()

    # --------------------------------------------------------
    # Scale each modality independently
    # --------------------------------------------------------

    (
        text_train_scaled,
        text_val_scaled,
        text_test_scaled,
        image_train_scaled,
        image_val_scaled,
        image_test_scaled,
        text_scaler,
        image_scaler,
    ) = scale_features(
        text_train,
        text_val,
        text_test,
        image_train,
        image_val,
        image_test,
    )

    # --------------------------------------------------------
    # Project features
    # --------------------------------------------------------

    (
        text_train_projected,
        text_val_projected,
        text_test_projected,
        image_train_projected,
        image_val_projected,
        image_test_projected,
    ) = project_features(
        text_train_scaled,
        text_val_scaled,
        text_test_scaled,
        image_train_scaled,
        image_val_scaled,
        image_test_scaled,
    )

    # --------------------------------------------------------
    # Fuse
    # --------------------------------------------------------

    (
        X_train,
        X_val,
        X_test,
    ) = fuse(
        text_train_projected,
        text_val_projected,
        text_test_projected,
        image_train_projected,
        image_val_projected,
        image_test_projected,
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    model = train_model(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    val_results = evaluate(
        model,
        X_val,
        y_val,
        "validation",
    )

    test_results = evaluate(
        model,
        X_test,
        y_test,
        "test",
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    model_path = (
        MODEL_DIR /
        "fakeddit_multimodal_fusion.joblib"
    )

    joblib.dump(
        {
            "model": model,
            "text_scaler": text_scaler,
            "image_scaler": image_scaler,
        },
        model_path,
    )

    # --------------------------------------------------------
    # Save fused features
    # --------------------------------------------------------

    np.save(
        MODEL_DIR /
        "fakeddit_multimodal_train_features.npy",
        X_train,
    )

    np.save(
        MODEL_DIR /
        "fakeddit_multimodal_validation_features.npy",
        X_val,
    )

    np.save(
        MODEL_DIR /
        "fakeddit_multimodal_test_features.npy",
        X_test,
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results = {
        "phase": "Phase 5 — Multimodal Intelligence",
        "experiment": "Text + Image early fusion",
        "dataset": "Fakeddit",
        "dataset_size": {
            "train": len(y_train),
            "validation": len(y_val),
            "test": len(y_test),
        },
        "modalities": {
            "text": {
                "encoder": "DistilBERT",
                "representation_dimension": int(
                    text_train.shape[1]
                ),
                "projected_dimension": int(
                    text_train_projected.shape[1]
                ),
            },
            "image": {
                "feature_extractor": "HOG",
                "representation_dimension": int(
                    image_train.shape[1]
                ),
                "projected_dimension": int(
                    image_train_projected.shape[1]
                ),
            },
        },
        "fusion": {
            "method": "concatenation",
            "fused_dimension": int(
                X_train.shape[1]
            ),
        },
        "classifier": {
            "type": "LogisticRegression",
            "C": 0.5,
            "class_weight": "balanced",
            "random_state": RANDOM_STATE,
        },
        "validation": val_results,
        "test": test_results,
    }

    results_path = (
        RESULTS_DIR /
        "fakeddit_multimodal_fusion_results.json"
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

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("MULTIMODAL FUSION COMPLETE")
    print("=" * 80)

    print(
        f"Saved model   : {model_path}"
    )

    print(
        f"Saved results : {results_path}"
    )

    print()
    print(
        "TEXT-ONLY → IMAGE-ONLY → MULTIMODAL"
    )

    print(
        "Phase 5 multimodal experiment completed."
    )


if __name__ == "__main__":
    main()