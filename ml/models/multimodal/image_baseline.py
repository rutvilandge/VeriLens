from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from PIL import Image
from skimage.feature import hog

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(
    "ml/datasets/multimodal/fakeddit/processed/valid_subset"
)

IMAGE_ROOT = ROOT / "images"

TRAIN_FILE = ROOT / "train.csv"
VAL_FILE = ROOT / "validation.csv"
TEST_FILE = ROOT / "test.csv"

OUTPUT_DIR = Path("ml/models/multimodal/saved")
RESULTS_DIR = Path("ml/evaluation/multimodal")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SIZE = (128, 128)

RANDOM_STATE = 42


# ============================================================
# IMAGE FEATURE EXTRACTION
# ============================================================

def extract_image_features(split):

    csv_path = {
        "train": TRAIN_FILE,
        "validation": VAL_FILE,
        "test": TEST_FILE,
    }[split]

    image_dir = IMAGE_ROOT / split

    df = pd.read_csv(csv_path)

    features = []
    labels = []

    total = len(df)

    print()
    print("=" * 80)
    print(f"EXTRACTING IMAGE FEATURES — {split.upper()}")
    print("=" * 80)

    for index, row in df.iterrows():

        image_id = str(row["id"])
        image_path = image_dir / f"{image_id}.jpg"

        if not image_path.exists():
            raise FileNotFoundError(
                f"Missing image: {image_path}"
            )

        with Image.open(image_path) as image:

            image = image.convert("RGB")
            image = image.resize(
                IMAGE_SIZE,
                Image.Resampling.BILINEAR,
            )

            image_array = np.asarray(
                image,
                dtype=np.float32,
            ) / 255.0

        # HOG feature extraction
        feature = hog(
            image_array,
            orientations=9,
            pixels_per_cell=(16, 16),
            cells_per_block=(2, 2),
            block_norm="L2-Hys",
            channel_axis=-1,
        )

        features.append(feature)
        labels.append(int(row["2_way_label"]))

        processed = index + 1

        if processed % 500 == 0 or processed == total:
            print(
                f"  Processed {processed:,}/{total:,}"
            )

    X = np.asarray(features, dtype=np.float32)
    y = np.asarray(labels, dtype=np.int64)

    print(f"Feature shape: {X.shape}")
    print(f"Labels shape : {y.shape}")

    return X, y


# ============================================================
# TRAIN CLASSIFIER
# ============================================================

def train_classifier(X_train, y_train):

    print()
    print("=" * 80)
    print("TRAINING IMAGE-ONLY CLASSIFIER")
    print("=" * 80)

    classifier = LogisticRegression(
        C=1.0,
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        solver="liblinear",
    )

    classifier.fit(
        X_train,
        y_train,
    )

    return classifier


# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    classifier,
    X,
    y,
    split_name,
):

    predictions = classifier.predict(X)

    probabilities = classifier.predict_proba(X)[:, 1]

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

    print(f"Accuracy       : {accuracy:.4f}")
    print(f"Macro Precision: {precision:.4f}")
    print(f"Macro Recall   : {recall:.4f}")
    print(f"Macro F1       : {macro_f1:.4f}")
    print(f"Weighted F1    : {weighted_f1:.4f}")
    print(f"ROC-AUC        : {roc_auc:.4f}")

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
    print("VERILENS PHASE 5 — IMAGE-ONLY BASELINE")
    print("=" * 80)

    # --------------------------------------------------------
    # Extract features
    # --------------------------------------------------------

    X_train, y_train = extract_image_features(
        "train"
    )

    X_val, y_val = extract_image_features(
        "validation"
    )

    X_test, y_test = extract_image_features(
        "test"
    )

    print()
    print("=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)

    print(f"Train features      : {X_train.shape}")
    print(f"Validation features : {X_val.shape}")
    print(f"Test features       : {X_test.shape}")

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    classifier = train_classifier(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    val_results = evaluate(
        classifier,
        X_val,
        y_val,
        "validation",
    )

    test_results = evaluate(
        classifier,
        X_test,
        y_test,
        "test",
    )

    # --------------------------------------------------------
    # Save classifier
    # --------------------------------------------------------

    model_path = (
        OUTPUT_DIR
        / "fakeddit_image_hog_logistic_regression.joblib"
    )

    joblib.dump(
        classifier,
        model_path,
    )

    # --------------------------------------------------------
    # Save features
    # --------------------------------------------------------

    np.save(
        OUTPUT_DIR / "fakeddit_image_train_features.npy",
        X_train,
    )

    np.save(
        OUTPUT_DIR / "fakeddit_image_validation_features.npy",
        X_val,
    )

    np.save(
        OUTPUT_DIR / "fakeddit_image_test_features.npy",
        X_test,
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results = {
        "phase": "Phase 5 — Multimodal Intelligence",
        "experiment": "Image-only baseline",
        "dataset": "Fakeddit",
        "dataset_size": {
            "train": len(y_train),
            "validation": len(y_val),
            "test": len(y_test),
        },
        "model": {
            "feature_extractor": "HOG",
            "classifier": "LogisticRegression",
            "image_size": list(IMAGE_SIZE),
            "orientations": 9,
            "pixels_per_cell": [16, 16],
            "cells_per_block": [2, 2],
            "feature_dimension": int(X_train.shape[1]),
            "random_state": RANDOM_STATE,
        },
        "validation": val_results,
        "test": test_results,
    }

    results_path = (
        RESULTS_DIR
        / "fakeddit_image_baseline_results.json"
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
    print("IMAGE-ONLY BASELINE COMPLETE")
    print("=" * 80)

    print(
        f"Saved classifier : {model_path}"
    )

    print(
        f"Saved results    : {results_path}"
    )

    print()
    print(
        "NEXT:"
    )
    print(
        "Text + Image → Multimodal Fusion"
    )


if __name__ == "__main__":
    main()