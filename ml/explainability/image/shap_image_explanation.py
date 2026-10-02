from pathlib import Path
import json

import joblib
import numpy as np
import shap
from PIL import Image
from skimage.feature import hog


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = Path(
    "ml/models/vision/saved/cifake_hog_logistic_regression.joblib"
)

OUTPUT_DIR = Path(
    "ml/explainability/artifacts"
)

OUTPUT_PATH = OUTPUT_DIR / "shap_image_explanations.json"

IMAGE_ROOT_CANDIDATES = [
    Path("ml/datasets/vision/cifake/processed"),
    Path("ml/datasets/vision/cifake/raw"),
]


# ============================================================
# CONFIGURATION
# ============================================================

IMAGE_SIZE = (32, 32)

HOG_CONFIG = {
    "orientations": 9,
    "pixels_per_cell": (4, 4),
    "cells_per_block": (2, 2),
    "block_norm": "L2-Hys",
}

BACKGROUND_SIZE = 100
EXPLAIN_SAMPLES = 20
TOP_FEATURES = 20


# ============================================================
# HELPERS
# ============================================================

def find_image_files():
    """Find CIFAKE image files."""

    extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    image_files = []

    for root in IMAGE_ROOT_CANDIDATES:

        if not root.exists():
            continue

        for path in root.rglob("*"):

            if (
                path.is_file()
                and path.suffix.lower() in extensions
            ):
                image_files.append(path)

    return sorted(image_files)


def load_image_features(image_path):
    """
    Reproduce the exact HOG preprocessing used
    by the Phase 4 CIFAKE model.
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
        orientations=HOG_CONFIG["orientations"],
        pixels_per_cell=HOG_CONFIG["pixels_per_cell"],
        cells_per_block=HOG_CONFIG["cells_per_block"],
        block_norm=HOG_CONFIG["block_norm"],
        channel_axis=-1,
    )

    return features


def find_label_from_path(image_path):
    """Infer the dataset label from directory names."""

    parts = [
        part.lower()
        for part in image_path.parts
    ]

    real_names = {
        "real",
        "0",
        "class0",
    }

    fake_names = {
        "fake",
        "ai",
        "generated",
        "synthetic",
        "1",
        "class1",
    }

    for part in reversed(parts):

        if part in real_names:
            return 0

        if part in fake_names:
            return 1

    return None


def feature_description(feature_index):
    """
    HOG features represent localized gradient/orientation
    patterns rather than individual pixels.
    """

    return (
        f"HOG feature {feature_index} "
        f"(localized edge/orientation pattern)"
    )


def get_top_features(
    shap_values,
    top_k,
):
    """Return strongest SHAP features."""

    absolute_values = np.abs(
        shap_values
    )

    top_indices = np.argsort(
        absolute_values
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        results.append(
            {
                "feature_index": int(index),
                "description": feature_description(
                    int(index)
                ),
                "shap_value": float(
                    shap_values[index]
                ),
                "absolute_shap_value": float(
                    absolute_values[index]
                ),
            }
        )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VERILENS - SHAP IMAGE EXPLAINABILITY")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # 1. LOAD MODEL
    # ========================================================

    print(
        "\n[1/7] Loading CIFAKE vision model..."
    )

    model = joblib.load(
        MODEL_PATH
    )

    print(
        f"Model: {MODEL_PATH}"
    )

    print(
        f"Model type: "
        f"{type(model).__name__}"
    )

    print(
        f"Model classes: "
        f"{model.classes_}"
    )

    # ========================================================
    # 2. FIND IMAGES
    # ========================================================

    print(
        "\n[2/7] Searching for CIFAKE images..."
    )

    image_files = find_image_files()

    print(
        f"Images discovered: "
        f"{len(image_files)}"
    )

    if len(image_files) == 0:

        raise FileNotFoundError(
            "\nNo CIFAKE images were found.\n\n"
            "Expected images under:\n"
            "ml/datasets/vision/cifake/processed\n"
            "or\n"
            "ml/datasets/vision/cifake/raw\n"
        )

    # ========================================================
    # 3. EXTRACT HOG FEATURES
    # ========================================================

    print(
        "\n[3/7] Extracting HOG features..."
    )

    all_features = []
    valid_paths = []
    labels = []

    for index, image_path in enumerate(
        image_files
    ):

        try:

            features = load_image_features(
                image_path
            )

            all_features.append(
                features
            )

            valid_paths.append(
                image_path
            )

            labels.append(
                find_label_from_path(
                    image_path
                )
            )

        except Exception as error:

            print(
                f"Skipping {image_path}: "
                f"{error}"
            )

        if (
            index + 1
        ) % 500 == 0:

            print(
                f"Processed "
                f"{index + 1}/"
                f"{len(image_files)}"
            )

    if len(all_features) == 0:

        raise RuntimeError(
            "No images could be converted into HOG features."
        )

    X = np.asarray(
        all_features,
        dtype=np.float32,
    )

    labels = np.asarray(
        labels,
        dtype=object,
    )

    print(
        f"\nFeature matrix: "
        f"{X.shape}"
    )

    # ========================================================
    # VALIDATE DIMENSIONS
    # ========================================================

    expected_features = model.coef_.shape[1]

    if X.shape[1] != expected_features:

        raise ValueError(
            "\nHOG feature dimension mismatch.\n"
            f"Generated: {X.shape[1]}\n"
            f"Model expects: {expected_features}\n"
        )

    print(
        f"HOG feature dimension verified: "
        f"{expected_features}"
    )

    # ========================================================
    # SELECT SAMPLES
    # ========================================================

    background_size = min(
        BACKGROUND_SIZE,
        X.shape[0],
    )

    explain_samples = min(
        EXPLAIN_SAMPLES,
        X.shape[0],
    )

    X_background = X[
        :background_size
    ]

    X_explain = X[
        :explain_samples
    ]

    print(
        f"\nBackground samples: "
        f"{background_size}"
    )

    print(
        f"Samples to explain: "
        f"{explain_samples}"
    )

    # ========================================================
    # 4. CREATE SHAP EXPLAINER
    # ========================================================

    print(
        "\n[4/7] Creating SHAP LinearExplainer..."
    )

    explainer = shap.LinearExplainer(
        model,
        X_background,
    )

    print(
        "SHAP LinearExplainer created successfully."
    )

    # ========================================================
    # 5. CALCULATE SHAP VALUES
    # ========================================================

    print(
        "\n[5/7] Calculating SHAP values..."
    )

    explanation = explainer(
        X_explain
    )

    if hasattr(
        explanation,
        "values",
    ):

        shap_values = np.asarray(
            explanation.values
        )

    else:

        shap_values = np.asarray(
            explanation
        )

    print(
        f"Raw SHAP shape: "
        f"{shap_values.shape}"
    )

    n_samples = X_explain.shape[0]
    n_features = X_explain.shape[1]
    n_classes = len(model.classes_)

    # ========================================================
    # HANDLE BINARY CLASSIFICATION
    # ========================================================

    if n_classes == 2:

        print(
            "\nBinary classification detected."
        )

        print(
            "Normalizing SHAP values for two classes..."
        )

        if shap_values.ndim == 2:

            # SHAP returned:
            # samples x features
            positive_class_values = (
                shap_values
            )

        elif shap_values.ndim == 3:

            if (
                shap_values.shape[0] == n_samples
                and shap_values.shape[1] == n_features
                and shap_values.shape[2] == 1
            ):

                positive_class_values = (
                    shap_values[:, :, 0]
                )

            elif (
                shap_values.shape[0] == n_samples
                and shap_values.shape[1] == 1
                and shap_values.shape[2] == n_features
            ):

                positive_class_values = (
                    shap_values[:, 0, :]
                )

            else:

                raise ValueError(
                    "Unexpected binary SHAP shape: "
                    f"{shap_values.shape}"
                )

        else:

            raise ValueError(
                "Unexpected binary SHAP dimensions: "
                f"{shap_values.shape}"
            )

        # For binary linear classification:
        #
        # class 0 contribution = -class 1 contribution
        #
        # class 1 is the positive class.
        class_0_values = (
            -positive_class_values
        )

        class_1_values = (
            positive_class_values
        )

        normalized_shap_values = np.stack(
            [
                class_0_values,
                class_1_values,
            ],
            axis=-1,
        )

    # ========================================================
    # HANDLE MULTICLASS FALLBACK
    # ========================================================

    else:

        print(
            "\nMulticlass classification detected."
        )

        if shap_values.ndim == 2:

            shap_values = (
                shap_values[:, :, np.newaxis]
            )

        if shap_values.ndim != 3:

            raise ValueError(
                "Unexpected multiclass SHAP shape: "
                f"{shap_values.shape}"
            )

        if (
            shap_values.shape[0] == n_samples
            and shap_values.shape[1] == n_features
            and shap_values.shape[2] == n_classes
        ):

            normalized_shap_values = (
                shap_values
            )

        elif (
            shap_values.shape[0] == n_samples
            and shap_values.shape[1] == n_classes
            and shap_values.shape[2] == n_features
        ):

            normalized_shap_values = (
                np.transpose(
                    shap_values,
                    (0, 2, 1),
                )
            )

        else:

            raise ValueError(
                "Unable to normalize multiclass SHAP shape: "
                f"{shap_values.shape}"
            )

    shap_values = normalized_shap_values

    print(
        f"Normalized SHAP shape: "
        f"{shap_values.shape}"
    )

    # ========================================================
    # 6. GLOBAL EXPLANATIONS
    # ========================================================

    print(
        "\n[6/7] Generating global image explanations..."
    )

    global_explanations = {}

    for class_position, class_label in enumerate(
        model.classes_
    ):

        class_values = shap_values[
            :,
            :,
            class_position,
        ]

        top_features = get_top_features(
            class_values.reshape(
                -1,
                n_features,
            ).mean(axis=0),
            TOP_FEATURES,
        )

        mean_absolute = np.mean(
            np.abs(class_values),
            axis=0,
        )

        mean_signed = np.mean(
            class_values,
            axis=0,
        )

        top_indices = np.argsort(
            mean_absolute
        )[::-1][:TOP_FEATURES]

        top_features = []

        for feature_index in top_indices:

            top_features.append(
                {
                    "feature_index": int(
                        feature_index
                    ),
                    "description": feature_description(
                        int(feature_index)
                    ),
                    "mean_absolute_shap": float(
                        mean_absolute[
                            feature_index
                        ]
                    ),
                    "mean_shap": float(
                        mean_signed[
                            feature_index
                        ]
                    ),
                }
            )

        global_explanations[
            str(class_label)
        ] = {
            "top_features": top_features
        }

    # ========================================================
    # LOCAL EXPLANATIONS
    # ========================================================

    print(
        "Generating local image explanations..."
    )

    predictions = model.predict(
        X_explain
    )

    probabilities = model.predict_proba(
        X_explain
    )

    local_explanations = []

    for sample_index in range(
        explain_samples
    ):

        predicted_class = predictions[
            sample_index
        ]

        class_position = list(
            model.classes_
        ).index(
            predicted_class
        )

        sample_shap = shap_values[
            sample_index,
            :,
            class_position,
        ]

        # Positive contributions
        positive_indices = np.argsort(
            sample_shap
        )[::-1]

        positive_features = []

        for feature_index in (
            positive_indices
        ):

            value = sample_shap[
                feature_index
            ]

            if value <= 0:
                continue

            positive_features.append(
                {
                    "feature_index": int(
                        feature_index
                    ),
                    "description": feature_description(
                        int(feature_index)
                    ),
                    "shap_value": float(
                        value
                    ),
                }
            )

            if len(
                positive_features
            ) >= 10:

                break

        # Negative contributions
        negative_indices = np.argsort(
            sample_shap
        )

        negative_features = []

        for feature_index in (
            negative_indices
        ):

            value = sample_shap[
                feature_index
            ]

            if value >= 0:
                continue

            negative_features.append(
                {
                    "feature_index": int(
                        feature_index
                    ),
                    "description": feature_description(
                        int(feature_index)
                    ),
                    "shap_value": float(
                        value
                    ),
                }
            )

            if len(
                negative_features
            ) >= 10:

                break

        probability_map = {
            str(class_label): float(
                probabilities[
                    sample_index,
                    class_position,
                ]
            )
            for class_position, class_label
            in enumerate(
                model.classes_
            )
        }

        local_explanations.append(
            {
                "sample_index": int(
                    sample_index
                ),
                "image_path": str(
                    valid_paths[
                        sample_index
                    ]
                ),
                "dataset_label": (
                    None
                    if labels[
                        sample_index
                    ] is None
                    else int(
                        labels[
                            sample_index
                        ]
                    )
                ),
                "predicted_class": int(
                    predicted_class
                ),
                "class_probabilities": probability_map,
                "positive_contributions": positive_features,
                "negative_contributions": negative_features,
            }
        )

    # ========================================================
    # BUILD ARTIFACT
    # ========================================================

    artifact = {
        "project": "VeriLens",

        "phase": "Phase 6 - Explainable AI",

        "component": "Image Explainability",

        "method": "SHAP LinearExplainer",

        "model": {
            "type": type(model).__name__,
            "path": str(MODEL_PATH),
            "classes": [
                int(label)
                for label in model.classes_
            ],
            "feature_count": int(
                expected_features
            ),
        },

        "image_preprocessing": {
            "resize": list(
                IMAGE_SIZE
            ),
            "hog": HOG_CONFIG,
        },

        "background": {
            "samples": int(
                background_size
            ),
        },

        "explained_samples": int(
            explain_samples
        ),

        "dataset_images_discovered": int(
            len(image_files)
        ),

        "valid_images_processed": int(
            len(valid_paths)
        ),

        "global_feature_importance": (
            global_explanations
        ),

        "local_explanations": (
            local_explanations
        ),

        "interpretation_notes": [
            "SHAP values describe how HOG features contribute to the model prediction.",
            "HOG features represent localized edge and gradient-orientation patterns rather than individual pixels.",
            "Positive SHAP values support the selected class.",
            "Negative SHAP values push the prediction away from the selected class.",
            "The explanation describes model behavior and does not prove that an image is genuinely AI-generated or real.",
            "The CIFAKE model was trained on a specific synthetic-image distribution and should not be interpreted as a universal AI-image detector.",
        ],
    }

    # ========================================================
    # 7. SAVE ARTIFACT
    # ========================================================

    print(
        "\n[7/7] Saving image SHAP artifact..."
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            artifact,
            file,
            indent=2,
        )

    print(
        f"\nSaved successfully:\n"
        f"{OUTPUT_PATH}"
    )

    # ========================================================
    # CONSOLE SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "TOP IMAGE SHAP FEATURES BY CLASS"
    )

    print(
        "=" * 70
    )

    for class_label, data in (
        global_explanations.items()
    ):

        print(
            f"\nClass {class_label}"
        )

        for feature in data[
            "top_features"
        ][:10]:

            print(
                f"  Feature "
                f"{feature['feature_index']:<5} "
                f"| mean |SHAP| = "
                f"{feature['mean_absolute_shap']:.6f} "
                f"| mean SHAP = "
                f"{feature['mean_shap']:+.6f}"
            )

    print(
        "\n" + "=" * 70
    )

    print(
        "SHAP IMAGE EXPLAINABILITY COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()