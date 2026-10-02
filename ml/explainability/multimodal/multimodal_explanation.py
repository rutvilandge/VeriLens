from pathlib import Path
import json

import joblib
import numpy as np
import shap


# ============================================================
# VERILENS
# PHASE 6.4 — MULTIMODAL EXPLAINABILITY
# ============================================================


# ============================================================
# PATHS
# ============================================================

ARTIFACT_PATH = Path(
    "ml/models/multimodal/saved/fakeddit_multimodal_fusion.joblib"
)

OUTPUT_DIR = Path(
    "ml/explainability/artifacts"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "multimodal_explanations.json"
)

FEATURE_ROOT = Path(
    "ml/models/multimodal/saved"
)


# ============================================================
# PHASE 5 ARCHITECTURE
# ============================================================

TEXT_ORIGINAL_DIM = 768
IMAGE_ORIGINAL_DIM = 1764

TEXT_FUSED_DIM = 256
IMAGE_FUSED_DIM = 256

TOTAL_FUSED_DIM = (
    TEXT_FUSED_DIM
    + IMAGE_FUSED_DIM
)


# ============================================================
# SHAP CONFIGURATION
# ============================================================

BACKGROUND_SIZE = 100
EXPLAIN_SAMPLES = 25
TOP_FEATURES = 15


# ============================================================
# POSSIBLE FILE NAMES
# ============================================================

TEXT_CANDIDATES = [
    "fakeddit_text_test_embeddings.npy",
    "fakeddit_text_test_embeddings_distilbert.npy",
    "fakeddit_text_test_features.npy",
    "fakeddit_text_test.npy",
    "text_test_embeddings.npy",
    "text_test_features.npy",
    "text_test.npy",
]

IMAGE_CANDIDATES = [
    "fakeddit_image_test_features.npy",
    "fakeddit_image_test_hog_features.npy",
    "fakeddit_image_test.npy",
    "image_test_features.npy",
    "image_test_hog_features.npy",
    "image_test.npy",
]

FUSED_CANDIDATES = [
    "fakeddit_fused_test_features.npy",
    "fakeddit_multimodal_fused_test.npy",
    "fakeddit_multimodal_test_features.npy",
    "fused_test_features.npy",
    "multimodal_test_features.npy",
]


# ============================================================
# FILE HELPERS
# ============================================================

def find_candidate(
    root,
    candidates,
):
    """
    Search direct path and recursively for candidate files.
    """

    for candidate in candidates:

        direct = root / candidate

        if direct.exists():

            return direct

    for candidate in candidates:

        matches = list(
            root.rglob(candidate)
        )

        if matches:

            return matches[0]

    return None


def list_npy_files(root):
    """List available NumPy arrays."""

    return sorted(
        root.rglob("*.npy")
    )


def load_npy(path):
    """Load a NumPy feature array."""

    array = np.load(
        path,
        allow_pickle=False,
    )

    return np.asarray(
        array,
        dtype=np.float32,
    )


# ============================================================
# FEATURE DESCRIPTIONS
# ============================================================

def text_feature_description(
    index,
):
    return (
        f"Text embedding dimension {index}"
    )


def image_feature_description(
    index,
):
    return (
        f"Image HOG dimension {index}"
    )


# ============================================================
# SHAP NORMALIZATION
# ============================================================

def normalize_shap_values(
    raw_values,
    n_samples,
    n_features,
    n_classes,
):
    """
    Normalize SHAP output to:

        samples × features × classes

    Handles binary Logistic Regression.
    """

    if hasattr(
        raw_values,
        "values",
    ):

        raw_values = raw_values.values

    values = np.asarray(
        raw_values
    )

    # --------------------------------------------------------
    # Binary SHAP output
    # --------------------------------------------------------

    if values.ndim == 2:

        positive_class_values = values

        if n_classes == 2:

            class_0 = (
                -positive_class_values
            )

            class_1 = (
                positive_class_values
            )

            return np.stack(
                [
                    class_0,
                    class_1,
                ],
                axis=-1,
            )

        return values[
            :,
            :,
            np.newaxis,
        ]

    # --------------------------------------------------------
    # 3D output
    # --------------------------------------------------------

    if values.ndim == 3:

        # samples × features × classes
        if (
            values.shape[0] == n_samples
            and values.shape[1] == n_features
            and values.shape[2] == n_classes
        ):

            return values

        # samples × classes × features
        if (
            values.shape[0] == n_samples
            and values.shape[1] == n_classes
            and values.shape[2] == n_features
        ):

            return np.transpose(
                values,
                (0, 2, 1),
            )

    raise ValueError(
        "Unexpected SHAP output shape.\n"
        f"Received: {values.shape}\n"
        f"Samples: {n_samples}\n"
        f"Features: {n_features}\n"
        f"Classes: {n_classes}"
    )


# ============================================================
# MODALITY SUMMARY
# ============================================================

def modality_summary(
    sample_shap,
):
    """
    Split the fused SHAP vector into:

        Text = first 256
        Image = last 256
    """

    text_values = sample_shap[
        :TEXT_FUSED_DIM
    ]

    image_values = sample_shap[
        TEXT_FUSED_DIM:
        TOTAL_FUSED_DIM
    ]

    text_absolute = float(
        np.sum(
            np.abs(
                text_values
            )
        )
    )

    image_absolute = float(
        np.sum(
            np.abs(
                image_values
            )
        )
    )

    total_absolute = (
        text_absolute
        + image_absolute
    )

    if total_absolute > 0:

        text_share = (
            text_absolute
            / total_absolute
        )

        image_share = (
            image_absolute
            / total_absolute
        )

    else:

        text_share = 0.0
        image_share = 0.0

    return {
        "text_absolute_shap": (
            text_absolute
        ),
        "image_absolute_shap": (
            image_absolute
        ),
        "text_contribution_share": (
            float(text_share)
        ),
        "image_contribution_share": (
            float(image_share)
        ),
        "text_signed_shap": float(
            np.sum(
                text_values
            )
        ),
        "image_signed_shap": float(
            np.sum(
                image_values
            )
        ),
    }


# ============================================================
# TOP LOCAL FEATURES
# ============================================================

def local_feature_explanation(
    sample_shap,
    modality,
):
    """
    Extract strongest positive and negative
    features for one modality.
    """

    if modality == "text":

        values = sample_shap[
            :TEXT_FUSED_DIM
        ]

        offset = 0

        describe = (
            text_feature_description
        )

    else:

        values = sample_shap[
            TEXT_FUSED_DIM:
            TOTAL_FUSED_DIM
        ]

        offset = TEXT_FUSED_DIM

        describe = (
            image_feature_description
        )

    positive_order = np.argsort(
        values
    )[::-1]

    negative_order = np.argsort(
        values
    )

    positive = []

    negative = []

    for index in positive_order:

        value = float(
            values[index]
        )

        if value <= 0:

            continue

        positive.append(
            {
                "feature_index": int(
                    index
                ),
                "global_feature_index": int(
                    index + offset
                ),
                "description": describe(
                    int(index)
                ),
                "shap_value": value,
            }
        )

        if len(
            positive
        ) >= 10:

            break

    for index in negative_order:

        value = float(
            values[index]
        )

        if value >= 0:

            continue

        negative.append(
            {
                "feature_index": int(
                    index
                ),
                "global_feature_index": int(
                    index + offset
                ),
                "description": describe(
                    int(index)
                ),
                "shap_value": value,
            }
        )

        if len(
            negative
        ) >= 10:

            break

    return {
        "positive": positive,
        "negative": negative,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "VERILENS - MULTIMODAL SHAP EXPLAINABILITY"
    )
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # 1. LOAD SAVED PHASE 5 ARTIFACT
    # ========================================================

    print(
        "\n[1/7] Loading Phase 5 multimodal artifact..."
    )

    if not ARTIFACT_PATH.exists():

        raise FileNotFoundError(
            f"Artifact not found:\n"
            f"{ARTIFACT_PATH}"
        )

    artifact = joblib.load(
        ARTIFACT_PATH
    )

    if not isinstance(
        artifact,
        dict,
    ):

        raise ValueError(
            "Expected the Phase 5 multimodal artifact "
            "to be a dictionary."
        )

    print(
        f"Artifact keys: "
        f"{list(artifact.keys())}"
    )

    model = artifact["model"]

    text_scaler = artifact[
        "text_scaler"
    ]

    image_scaler = artifact[
        "image_scaler"
    ]

    print(
        f"Model type: "
        f"{type(model).__name__}"
    )

    print(
        f"Classes: "
        f"{model.classes_}"
    )

    print(
        f"Text scaler: "
        f"{type(text_scaler).__name__}"
    )

    print(
        f"Image scaler: "
        f"{type(image_scaler).__name__}"
    )

    # ========================================================
    # 2. LOCATE ORIGINAL PHASE 5 FEATURES
    # ========================================================

    print(
        "\n[2/7] Locating Phase 5 feature arrays..."
    )

    text_path = find_candidate(
        FEATURE_ROOT,
        TEXT_CANDIDATES,
    )

    image_path = find_candidate(
        FEATURE_ROOT,
        IMAGE_CANDIDATES,
    )

    fused_path = find_candidate(
        FEATURE_ROOT,
        FUSED_CANDIDATES,
    )

    print(
        f"Text file : {text_path}"
    )

    print(
        f"Image file: {image_path}"
    )

    print(
        f"Fused file: {fused_path}"
    )

    # ========================================================
    # If an already-fused matrix exists
    # ========================================================

    if fused_path is not None:

        print(
            "\nUsing saved fused feature matrix."
        )

        X_fused = load_npy(
            fused_path
        )

    else:

        if (
            text_path is None
            or image_path is None
        ):

            print(
                "\nAvailable .npy files:"
            )

            for path in list_npy_files(
                FEATURE_ROOT
            ):

                print(
                    f"  {path}"
                )

            raise FileNotFoundError(
                "\nCould not identify the Phase 5 "
                "text/image feature arrays.\n"
                "The available files are printed above."
            )

        # ====================================================
        # LOAD ORIGINAL FEATURES
        # ====================================================

        print(
            "\nLoading original text features..."
        )

        X_text_original = load_npy(
            text_path
        )

        print(
            f"Original text shape: "
            f"{X_text_original.shape}"
        )

        print(
            "\nLoading original image features..."
        )

        X_image_original = load_npy(
            image_path
        )

        print(
            f"Original image shape: "
            f"{X_image_original.shape}"
        )

        # ====================================================
        # VALIDATE SAMPLE COUNTS
        # ====================================================

        if (
            X_text_original.shape[0]
            !=
            X_image_original.shape[0]
        ):

            raise ValueError(
                "\nText/image sample count mismatch.\n"
                f"Text: {X_text_original.shape}\n"
                f"Image: {X_image_original.shape}"
            )

        # ====================================================
        # VALIDATE ORIGINAL DIMENSIONS
        # ====================================================

        if (
            X_text_original.shape[1]
            !=
            TEXT_ORIGINAL_DIM
        ):

            raise ValueError(
                "\nUnexpected text embedding dimension.\n"
                f"Expected: {TEXT_ORIGINAL_DIM}\n"
                f"Found: {X_text_original.shape[1]}"
            )

        if (
            X_image_original.shape[1]
            !=
            IMAGE_ORIGINAL_DIM
        ):

            raise ValueError(
                "\nUnexpected image HOG dimension.\n"
                f"Expected: {IMAGE_ORIGINAL_DIM}\n"
                f"Found: {X_image_original.shape[1]}"
            )

        # ====================================================
        # APPLY THE SAME SCALERS AS PHASE 5
        # ====================================================

        print(
            "\nApplying saved text scaler..."
        )

        X_text_scaled = (
            text_scaler.transform(
                X_text_original
            )
        )

        print(
            "\nApplying saved image scaler..."
        )

        X_image_scaled = (
            image_scaler.transform(
                X_image_original
            )
        )

        # ====================================================
        # APPLY THE SAME 256-D PROJECTION
        # ====================================================

        print(
            "\nApplying Phase 5 256-dimensional projection..."
        )

        X_text_projected = (
            X_text_scaled[
                :,
                :TEXT_FUSED_DIM
            ]
        )

        X_image_projected = (
            X_image_scaled[
                :,
                :IMAGE_FUSED_DIM
            ]
        )

        print(
            f"Projected text: "
            f"{X_text_projected.shape}"
        )

        print(
            f"Projected image: "
            f"{X_image_projected.shape}"
        )

        # ====================================================
        # FEATURE-LEVEL FUSION
        # ====================================================

        X_fused = np.concatenate(
            [
                X_text_projected,
                X_image_projected,
            ],
            axis=1,
        )

    # ========================================================
    # 3. VALIDATE FUSED FEATURES
    # ========================================================

    print(
        "\n[3/7] Validating fused feature matrix..."
    )

    print(
        f"Fused shape: "
        f"{X_fused.shape}"
    )

    if X_fused.ndim != 2:

        raise ValueError(
            "Fused feature matrix must be 2-dimensional."
        )

    if (
        X_fused.shape[1]
        !=
        TOTAL_FUSED_DIM
    ):

        raise ValueError(
            "\nUnexpected fused feature dimension.\n"
            f"Expected: {TOTAL_FUSED_DIM}\n"
            f"Found: {X_fused.shape[1]}"
        )

    model_features = (
        model.coef_.shape[1]
    )

    if (
        model_features
        !=
        TOTAL_FUSED_DIM
    ):

        raise ValueError(
            "\nModel and fused features do not match.\n"
            f"Model: {model_features}\n"
            f"Features: {TOTAL_FUSED_DIM}"
        )

    print(
        "Fusion architecture verified:"
    )

    print(
        f"  Text  = {TEXT_FUSED_DIM}"
    )

    print(
        f"  Image = {IMAGE_FUSED_DIM}"
    )

    print(
        f"  Total = {TOTAL_FUSED_DIM}"
    )

    # ========================================================
    # SAMPLE SELECTION
    # ========================================================

    background_size = min(
        BACKGROUND_SIZE,
        X_fused.shape[0],
    )

    explain_samples = min(
        EXPLAIN_SAMPLES,
        X_fused.shape[0],
    )

    X_background = X_fused[
        :background_size
    ]

    X_explain = X_fused[
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
    # 4. SHAP EXPLAINER
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
    # 5. CALCULATE SHAP
    # ========================================================

    print(
        "\n[5/7] Calculating SHAP values..."
    )

    explanation = explainer(
        X_explain
    )

    shap_values = normalize_shap_values(
        explanation,
        n_samples=X_explain.shape[0],
        n_features=X_explain.shape[1],
        n_classes=len(
            model.classes_
        ),
    )

    print(
        f"Normalized SHAP shape: "
        f"{shap_values.shape}"
    )

    # ========================================================
    # GLOBAL MODALITY IMPORTANCE
    # ========================================================

    print(
        "\nCalculating global modality importance..."
    )

    if len(
        model.classes_
    ) == 2:

        target_class_position = 1

    else:

        target_class_position = 0

    target_shap = shap_values[
        :,
        :,
        target_class_position,
    ]

    text_shap = target_shap[
        :,
        :TEXT_FUSED_DIM,
    ]

    image_shap = target_shap[
        :,
        TEXT_FUSED_DIM:
        TOTAL_FUSED_DIM,
    ]

    text_global = float(
        np.mean(
            np.abs(
                text_shap
            )
        )
    )

    image_global = float(
        np.mean(
            np.abs(
                image_shap
            )
        )
    )

    global_total = (
        text_global
        + image_global
    )

    if global_total > 0:

        text_share = (
            text_global
            / global_total
        )

        image_share = (
            image_global
            / global_total
        )

    else:

        text_share = 0.0
        image_share = 0.0

    # ========================================================
    # GLOBAL FEATURE IMPORTANCE
    # ========================================================

    text_feature_importance = np.mean(
        np.abs(
            text_shap
        ),
        axis=0,
    )

    image_feature_importance = np.mean(
        np.abs(
            image_shap
        ),
        axis=0,
    )

    top_text_indices = np.argsort(
        text_feature_importance
    )[::-1][:TOP_FEATURES]

    top_image_indices = np.argsort(
        image_feature_importance
    )[::-1][:TOP_FEATURES]

    top_text_features = []

    for index in top_text_indices:

        top_text_features.append(
            {
                "feature_index": int(
                    index
                ),
                "description": (
                    text_feature_description(
                        int(index)
                    )
                ),
                "mean_absolute_shap": float(
                    text_feature_importance[
                        index
                    ]
                ),
            }
        )

    top_image_features = []

    for index in top_image_indices:

        top_image_features.append(
            {
                "feature_index": int(
                    index
                ),
                "description": (
                    image_feature_description(
                        int(index)
                    )
                ),
                "mean_absolute_shap": float(
                    image_feature_importance[
                        index
                    ]
                ),
            }
        )

    # ========================================================
    # 6. LOCAL EXPLANATIONS
    # ========================================================

    print(
        "\n[6/7] Generating local multimodal explanations..."
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

        predicted_position = list(
            model.classes_
        ).index(
            predicted_class
        )

        sample_shap = shap_values[
            sample_index,
            :,
            predicted_position,
        ]

        summary = modality_summary(
            sample_shap
        )

        text_explanation = (
            local_feature_explanation(
                sample_shap,
                "text",
            )
        )

        image_explanation = (
            local_feature_explanation(
                sample_shap,
                "image",
            )
        )

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
                "predicted_class": int(
                    predicted_class
                ),
                "class_probabilities": (
                    probability_map
                ),
                "modality_contribution": (
                    summary
                ),
                "text_explanation": (
                    text_explanation
                ),
                "image_explanation": (
                    image_explanation
                ),
            }
        )

    # ========================================================
    # FINAL ARTIFACT
    # ========================================================

    final_artifact = {
        "project": "VeriLens",

        "phase": (
            "Phase 6 - Explainable AI"
        ),

        "component": (
            "Multimodal Explainability"
        ),

        "method": (
            "SHAP LinearExplainer"
        ),

        "source_artifact": str(
            ARTIFACT_PATH
        ),

        "model": {
            "type": type(model).__name__,
            "classes": [
                int(label)
                for label in model.classes_
            ],
            "feature_count": int(
                model_features
            ),
        },

        "phase_5_architecture": {
            "text_original_dimension": (
                TEXT_ORIGINAL_DIM
            ),
            "image_original_dimension": (
                IMAGE_ORIGINAL_DIM
            ),
            "text_projected_dimension": (
                TEXT_FUSED_DIM
            ),
            "image_projected_dimension": (
                IMAGE_FUSED_DIM
            ),
            "fusion_dimension": (
                TOTAL_FUSED_DIM
            ),
            "fusion_method": (
                "scaled feature concatenation"
            ),
        },

        "background_samples": int(
            background_size
        ),

        "explained_samples": int(
            explain_samples
        ),

        "global_modality_importance": {
            "text": {
                "mean_absolute_shap": (
                    text_global
                ),
                "contribution_share": float(
                    text_share
                ),
            },
            "image": {
                "mean_absolute_shap": (
                    image_global
                ),
                "contribution_share": float(
                    image_share
                ),
            },
        },

        "global_text_features": (
            top_text_features
        ),

        "global_image_features": (
            top_image_features
        ),

        "local_explanations": (
            local_explanations
        ),

        "interpretation_notes": [
            "SHAP explains the behavior of the trained multimodal classifier.",
            "The first 256 fused dimensions correspond to the scaled text representation.",
            "The final 256 fused dimensions correspond to the scaled image representation.",
            "Text and image contribution shares are calculated from absolute SHAP magnitude.",
            "A larger modality contribution means that modality had greater influence on that prediction; it does not mean that modality is more accurate.",
            "The multimodal fusion model uses feature-level concatenation followed by Logistic Regression.",
            "These explanations describe model behavior and should not be interpreted as proof of factual truth.",
        ],
    }

    # ========================================================
    # 7. SAVE
    # ========================================================

    print(
        "\n[7/7] Saving multimodal explanation artifact..."
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_artifact,
            file,
            indent=2,
        )

    print(
        f"\nSaved successfully:"
    )

    print(
        OUTPUT_PATH
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "GLOBAL MULTIMODAL CONTRIBUTION"
    )

    print(
        "=" * 70
    )

    print(
        f"Text contribution : "
        f"{text_share * 100:.2f}%"
    )

    print(
        f"Image contribution: "
        f"{image_share * 100:.2f}%"
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "TOP GLOBAL TEXT FEATURES"
    )

    print(
        "=" * 70
    )

    for feature in (
        top_text_features[:10]
    ):

        print(
            f"  {feature['description']:<40}"
            f"| mean |SHAP| = "
            f"{feature['mean_absolute_shap']:.6f}"
        )

    print(
        "\n" + "=" * 70
    )

    print(
        "TOP GLOBAL IMAGE FEATURES"
    )

    print(
        "=" * 70
    )

    for feature in (
        top_image_features[:10]
    ):

        print(
            f"  {feature['description']:<40}"
            f"| mean |SHAP| = "
            f"{feature['mean_absolute_shap']:.6f}"
        )

    print(
        "\n" + "=" * 70
    )

    print(
        "SHAP MULTIMODAL EXPLAINABILITY COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()