from pathlib import Path
import json
import random

import joblib
import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from skimage.feature import hog


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_DIR = (
    PROJECT_ROOT
    / "ml"
    / "datasets"
    / "vision"
    / "cifake"
)

CPU_SUBSET_DIR = (
    DATASET_DIR
    / "cpu_subset"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "vision"
    / "saved"
)

EVALUATION_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
)

MODEL_PATH = (
    MODEL_DIR
    / "cifake_hog_logistic_regression.joblib"
)

RESULTS_PATH = (
    EVALUATION_DIR
    / "cifake_hog_results.json"
)


# ============================================================
# Configuration
# ============================================================

SEED = 42

IMAGE_SIZE = (
    32,
    32,
)

HOG_ORIENTATIONS = 9

HOG_PIXELS_PER_CELL = (
    4,
    4,
)

HOG_CELLS_PER_BLOCK = (
    2,
    2,
)

MAX_ITER = 1000

C = 1.0

CLASS_TO_INDEX = {
    "real": 0,
    "fake": 1,
}


# ============================================================
# Reproducibility
# ============================================================

random.seed(SEED)

np.random.seed(SEED)


# ============================================================
# Image discovery
# ============================================================

def collect_images(
    split_directory: Path,
):
    """
    Collect image paths and labels from:

        split/
        ├── real/
        └── fake/
    """

    samples = []

    for class_name, label in (
        CLASS_TO_INDEX.items()
    ):

        class_directory = (
            split_directory
            / class_name
        )

        if not class_directory.exists():

            raise FileNotFoundError(
                f"Missing directory: "
                f"{class_directory}"
            )

        for image_path in sorted(
            class_directory.iterdir()
        ):

            if (
                image_path.is_file()
                and image_path.suffix.lower()
                in {
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".bmp",
                    ".webp",
                }
            ):

                samples.append(
                    (
                        image_path,
                        label,
                    )
                )

    random.Random(SEED).shuffle(
        samples
    )

    return samples


# ============================================================
# HOG feature extraction
# ============================================================

def extract_hog_features(
    image_path: Path,
):
    """
    Convert an image into a HOG feature vector.
    """

    image = Image.open(
        image_path
    ).convert("RGB")

    image = image.resize(
        IMAGE_SIZE
    )

    image_array = np.asarray(
        image,
        dtype=np.float32,
    ) / 255.0

    features = hog(
        image_array,
        orientations=HOG_ORIENTATIONS,
        pixels_per_cell=HOG_PIXELS_PER_CELL,
        cells_per_block=HOG_CELLS_PER_BLOCK,
        channel_axis=-1,
        block_norm="L2-Hys",
    )

    return features.astype(
        np.float32
    )


# ============================================================
# Build feature matrix
# ============================================================

def build_feature_matrix(
    samples,
    split_name,
):

    print()

    print(
        f"Extracting HOG features: "
        f"{split_name}"
    )

    features = []

    labels = []

    total = len(samples)

    for index, (
        image_path,
        label,
    ) in enumerate(samples, start=1):

        feature_vector = (
            extract_hog_features(
                image_path
            )
        )

        features.append(
            feature_vector
        )

        labels.append(label)

        if (
            index == 1
            or index % 1000 == 0
            or index == total
        ):

            print(
                f"  {index:,}/{total:,}"
            )

    feature_matrix = np.vstack(
        features
    )

    label_array = np.asarray(
        labels,
        dtype=np.int64,
    )

    print(
        f"Feature matrix: "
        f"{feature_matrix.shape}"
    )

    return (
        feature_matrix,
        label_array,
    )


# ============================================================
# Metrics
# ============================================================

def evaluate_model(
    model,
    features,
    labels,
):

    predictions = model.predict(
        features
    )

    probabilities = (
        model.predict_proba(
            features
        )[:, 1]
    )

    accuracy = accuracy_score(
        labels,
        predictions,
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            labels,
            predictions,
            average="macro",
            zero_division=0,
        )
    )

    roc_auc = roc_auc_score(
        labels,
        probabilities,
    )

    matrix = confusion_matrix(
        labels,
        predictions,
    )

    return {

        "accuracy":
            float(accuracy),

        "macro_precision":
            float(precision),

        "macro_recall":
            float(recall),

        "macro_f1":
            float(f1),

        "roc_auc":
            float(roc_auc),

        "confusion_matrix":
            matrix.tolist(),
    }


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)

    print(
        "VeriLens — CIFAKE HOG "
        "Computer Vision Baseline"
    )

    print("=" * 70)

    print()

    print(
        f"Dataset: "
        f"{CPU_SUBSET_DIR}"
    )

    print(
        f"Image size: "
        f"{IMAGE_SIZE[0]}x{IMAGE_SIZE[1]}"
    )

    print(
        f"HOG orientations: "
        f"{HOG_ORIENTATIONS}"
    )

    print(
        f"Pixels per cell: "
        f"{HOG_PIXELS_PER_CELL}"
    )

    print(
        f"Cells per block: "
        f"{HOG_CELLS_PER_BLOCK}"
    )

    # --------------------------------------------------------
    # Create directories
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Discover datasets
    # --------------------------------------------------------

    train_samples = collect_images(
        CPU_SUBSET_DIR / "train"
    )

    validation_samples = collect_images(
        CPU_SUBSET_DIR / "validation"
    )

    test_samples = collect_images(
        CPU_SUBSET_DIR / "test"
    )

    print()

    print("Dataset:")

    print(
        f"Train: "
        f"{len(train_samples):,}"
    )

    print(
        f"Validation: "
        f"{len(validation_samples):,}"
    )

    print(
        f"Test: "
        f"{len(test_samples):,}"
    )

    # --------------------------------------------------------
    # Feature extraction
    # --------------------------------------------------------

    (
        X_train,
        y_train,
    ) = build_feature_matrix(
        train_samples,
        "train",
    )

    (
        X_validation,
        y_validation,
    ) = build_feature_matrix(
        validation_samples,
        "validation",
    )

    (
        X_test,
        y_test,
    ) = build_feature_matrix(
        test_samples,
        "test",
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print()

    print("=" * 70)

    print(
        "TRAINING LOGISTIC REGRESSION"
    )

    print("=" * 70)

    model = LogisticRegression(
        C=C,
        max_iter=MAX_ITER,
        random_state=SEED,
        solver="liblinear",
    )

    model.fit(
        X_train,
        y_train,
    )

    print(
        "Training complete."
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validation_metrics = (
        evaluate_model(
            model,
            X_validation,
            y_validation,
        )
    )

    print()

    print("=" * 70)

    print("VALIDATION RESULTS")

    print("=" * 70)

    print(
        f"Accuracy: "
        f"{validation_metrics['accuracy']:.4f}"
    )

    print(
        f"Macro Precision: "
        f"{validation_metrics['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall: "
        f"{validation_metrics['macro_recall']:.4f}"
    )

    print(
        f"Macro F1: "
        f"{validation_metrics['macro_f1']:.4f}"
    )

    print(
        f"ROC-AUC: "
        f"{validation_metrics['roc_auc']:.4f}"
    )

    # --------------------------------------------------------
    # Test
    # --------------------------------------------------------

    test_metrics = evaluate_model(
        model,
        X_test,
        y_test,
    )

    print()

    print("=" * 70)

    print("TEST RESULTS")

    print("=" * 70)

    print(
        f"Accuracy: "
        f"{test_metrics['accuracy']:.4f}"
    )

    print(
        f"Macro Precision: "
        f"{test_metrics['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall: "
        f"{test_metrics['macro_recall']:.4f}"
    )

    print(
        f"Macro F1: "
        f"{test_metrics['macro_f1']:.4f}"
    )

    print(
        f"ROC-AUC: "
        f"{test_metrics['roc_auc']:.4f}"
    )

    print()

    print(
        "Confusion Matrix:"
    )

    for row in test_metrics[
        "confusion_matrix"
    ]:

        print(row)

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH,
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results = {

        "experiment":
            "cifake_hog_logistic_regression",

        "dataset":
            "CIFAKE",

        "dataset_note":
            (
                "This experiment uses "
                "the balanced 14,000-image "
                "CPU subset created from "
                "the CIFAKE benchmark."
            ),

        "classes":
            {
                "0": "real",
                "1": "fake",
            },

        "split_sizes":
            {
                "train":
                    len(train_samples),

                "validation":
                    len(validation_samples),

                "test":
                    len(test_samples),
            },

        "feature_extraction":
            {
                "method":
                    "Histogram of Oriented Gradients",

                "image_size":
                    list(IMAGE_SIZE),

                "orientations":
                    HOG_ORIENTATIONS,

                "pixels_per_cell":
                    list(
                        HOG_PIXELS_PER_CELL
                    ),

                "cells_per_block":
                    list(
                        HOG_CELLS_PER_BLOCK
                    ),

                "train_features":
                    list(
                        X_train.shape
                    ),
            },

        "model":
            {
                "algorithm":
                    "Logistic Regression",

                "C":
                    C,

                "solver":
                    "liblinear",

                "max_iter":
                    MAX_ITER,
            },

        "validation_metrics":
            validation_metrics,

        "test_metrics":
            test_metrics,

        "seed":
            SEED,

        "model_path":
            str(MODEL_PATH),
    }

    with RESULTS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
        )

    print()

    print("=" * 70)

    print(
        "COMPUTER VISION BASELINE COMPLETE"
    )

    print("=" * 70)

    print()

    print(
        f"Model saved to:"
    )

    print(
        MODEL_PATH
    )

    print()

    print(
        f"Results saved to:"
    )

    print(
        RESULTS_PATH
    )


if __name__ == "__main__":

    main()