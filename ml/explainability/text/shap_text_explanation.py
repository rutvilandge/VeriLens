from pathlib import Path
import json

import joblib
import numpy as np
import shap
from scipy.sparse import load_npz


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = Path(
    "ml/models/classical_ml/saved/logistic_regression_v2.joblib"
)

TRAIN_FEATURES_PATH = Path(
    "data/processed/tfidf/train_features.npz"
)

TEST_FEATURES_PATH = Path(
    "data/processed/tfidf/test_features.npz"
)

VECTORIZER_PATH = Path(
    "data/processed/tfidf/tfidf_vectorizer.joblib"
)

OUTPUT_DIR = Path("ml/explainability/artifacts")
OUTPUT_PATH = OUTPUT_DIR / "shap_text_explanations.json"


# ============================================================
# CONFIGURATION
# ============================================================

BACKGROUND_SIZE = 100
EXPLAIN_SAMPLES = 25
TOP_FEATURES = 20


ENGINEERED_FEATURES = [
    "char_count",
    "word_count",
    "sentence_count",
    "average_word_length",
    "uppercase_ratio",
    "punctuation_count",
    "question_mark_count",
    "exclamation_mark_count",
]


# ============================================================
# HELPERS
# ============================================================

def build_feature_names(vectorizer):
    """
    Build complete feature names:
    15,000 TF-IDF features + 8 engineered features.
    """

    tfidf_names = list(vectorizer.get_feature_names_out())

    feature_names = tfidf_names + ENGINEERED_FEATURES

    return feature_names


def normalize_shap_values(shap_values, n_samples, n_features, n_classes):
    """
    Normalize SHAP output across different SHAP versions.

    Expected final shape:
        (samples, features, classes)
    """

    # Newer SHAP versions may return an Explanation object.
    if hasattr(shap_values, "values"):
        shap_values = shap_values.values

    # Older SHAP versions may return a list:
    # one matrix per class.
    if isinstance(shap_values, list):

        arrays = [
            np.asarray(class_values)
            for class_values in shap_values
        ]

        return np.stack(arrays, axis=-1)

    values = np.asarray(shap_values)

    if values.ndim == 2:
        # Binary/single-output fallback.
        values = values[:, :, np.newaxis]

    elif values.ndim == 3:

        # Expected:
        # samples x features x classes
        if (
            values.shape[0] == n_samples
            and values.shape[1] == n_features
            and values.shape[2] == n_classes
        ):
            return values

        # Alternative:
        # samples x classes x features
        if (
            values.shape[0] == n_samples
            and values.shape[1] == n_classes
            and values.shape[2] == n_features
        ):
            return np.transpose(values, (0, 2, 1))

        # Alternative:
        # classes x samples x features
        if (
            values.shape[0] == n_classes
            and values.shape[1] == n_samples
            and values.shape[2] == n_features
        ):
            return np.transpose(values, (1, 2, 0))

    raise ValueError(
        "Unexpected SHAP output shape: "
        f"{values.shape}"
    )


def get_top_features(
    class_values,
    feature_names,
    top_k=20,
):
    """
    Return top features according to mean absolute SHAP value.
    """

    mean_abs = np.mean(
        np.abs(class_values),
        axis=0,
    )

    mean_signed = np.mean(
        class_values,
        axis=0,
    )

    top_indices = np.argsort(
        mean_abs
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        results.append(
            {
                "feature": feature_names[index],
                "mean_absolute_shap": float(
                    mean_abs[index]
                ),
                "mean_shap": float(
                    mean_signed[index]
                ),
            }
        )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VERILENS - SHAP TEXT EXPLAINABILITY")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print("\n[1/7] Loading Logistic Regression model...")

    model = joblib.load(MODEL_PATH)

    print(f"Model: {MODEL_PATH}")
    print(f"Model type: {type(model).__name__}")

    # --------------------------------------------------------
    # Load vectorizer
    # --------------------------------------------------------

    print("\n[2/7] Loading TF-IDF vectorizer...")

    vectorizer = joblib.load(VECTORIZER_PATH)

    print(
        f"TF-IDF vocabulary size: "
        f"{len(vectorizer.get_feature_names_out())}"
    )

    # --------------------------------------------------------
    # Build feature names
    # --------------------------------------------------------

    print("\n[3/7] Building feature names...")

    feature_names = build_feature_names(vectorizer)

    print(
        f"Total feature names: "
        f"{len(feature_names)}"
    )

    # --------------------------------------------------------
    # Load training and test features
    # --------------------------------------------------------

    print("\n[4/7] Loading sparse feature matrices...")

    X_train = load_npz(
        TRAIN_FEATURES_PATH
    )

    X_test = load_npz(
        TEST_FEATURES_PATH
    )

    print(
        f"Training matrix: "
        f"{X_train.shape}"
    )

    print(
        f"Test matrix: "
        f"{X_test.shape}"
    )

    # --------------------------------------------------------
    # Validate dimensions
    # --------------------------------------------------------

    expected_features = model.coef_.shape[1]

    if X_train.shape[1] != expected_features:
        raise ValueError(
            "Training feature dimension does not match model.\n"
            f"Training: {X_train.shape[1]}\n"
            f"Model: {expected_features}"
        )

    if X_test.shape[1] != expected_features:
        raise ValueError(
            "Test feature dimension does not match model.\n"
            f"Test: {X_test.shape[1]}\n"
            f"Model: {expected_features}"
        )

    if len(feature_names) != expected_features:
        raise ValueError(
            "Feature-name count does not match model.\n"
            f"Feature names: {len(feature_names)}\n"
            f"Model: {expected_features}"
        )

    # --------------------------------------------------------
    # Select small CPU-friendly subsets
    # --------------------------------------------------------

    background_size = min(
        BACKGROUND_SIZE,
        X_train.shape[0],
    )

    explain_samples = min(
        EXPLAIN_SAMPLES,
        X_test.shape[0],
    )

    print(
        f"\nUsing {background_size} "
        f"training samples as SHAP background."
    )

    print(
        f"Explaining {explain_samples} "
        f"test samples."
    )

    X_background = X_train[
        :background_size
    ].toarray()

    X_explain = X_test[
        :explain_samples
    ].toarray()

    # --------------------------------------------------------
    # Create SHAP LinearExplainer
    # --------------------------------------------------------

    print("\n[5/7] Creating SHAP LinearExplainer...")

    explainer = shap.LinearExplainer(
        model,
        X_background,
    )

    print("SHAP LinearExplainer created successfully.")

    # --------------------------------------------------------
    # Calculate SHAP values
    # --------------------------------------------------------

    print("\n[6/7] Calculating SHAP values...")

    explanation = explainer(
        X_explain
    )

    n_samples = X_explain.shape[0]
    n_features = X_explain.shape[1]
    n_classes = len(model.classes_)

    shap_values = normalize_shap_values(
        explanation,
        n_samples=n_samples,
        n_features=n_features,
        n_classes=n_classes,
    )

    print(
        f"Normalized SHAP shape: "
        f"{shap_values.shape}"
    )

    # --------------------------------------------------------
    # Generate global explanations
    # --------------------------------------------------------

    print("\nGenerating global feature importance...")

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
            class_values,
            feature_names,
            TOP_FEATURES,
        )

        global_explanations[
            str(class_label)
        ] = {
            "top_features": top_features
        }

    # --------------------------------------------------------
    # Generate local explanations
    # --------------------------------------------------------

    print("Generating local explanations...")

    predictions = model.predict(
        X_test[:explain_samples]
    )

    probabilities = model.predict_proba(
        X_test[:explain_samples]
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
        ).index(predicted_class)

        sample_shap = shap_values[
            sample_index,
            :,
            class_position,
        ]

        positive_indices = np.argsort(
            sample_shap
        )[::-1][:TOP_FEATURES]

        negative_indices = np.argsort(
            sample_shap
        )[:TOP_FEATURES]

        positive_features = []

        for index in positive_indices:

            value = sample_shap[index]

            if value <= 0:
                continue

            positive_features.append(
                {
                    "feature": feature_names[index],
                    "shap_value": float(value),
                }
            )

        negative_features = []

        for index in negative_indices:

            value = sample_shap[index]

            if value >= 0:
                continue

            negative_features.append(
                {
                    "feature": feature_names[index],
                    "shap_value": float(value),
                }
            )

        probability_map = {
            str(class_label): float(
                probabilities[
                    sample_index,
                    class_position,
                ]
            )
            for class_position, class_label
            in enumerate(model.classes_)
        }

        local_explanations.append(
            {
                "sample_index": int(
                    sample_index
                ),
                "predicted_class": int(
                    predicted_class
                ),
                "class_probabilities": probability_map,
                "positive_contributions": positive_features[
                    :10
                ],
                "negative_contributions": negative_features[
                    :10
                ],
            }
        )

    # --------------------------------------------------------
    # Create summary
    # --------------------------------------------------------

    artifact = {
        "project": "VeriLens",
        "phase": "Phase 6 - Explainable AI",
        "component": "Text Explainability",
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

        "background": {
            "source": str(
                TRAIN_FEATURES_PATH
            ),
            "samples": int(
                background_size
            ),
        },

        "explained_test_samples": int(
            explain_samples
        ),

        "feature_groups": {
            "tfidf_features": len(
                vectorizer.get_feature_names_out()
            ),
            "engineered_features": len(
                ENGINEERED_FEATURES
            ),
            "engineered_feature_names": ENGINEERED_FEATURES,
        },

        "global_feature_importance": global_explanations,

        "local_explanations": local_explanations,

        "interpretation_notes": [
            "SHAP values describe the contribution of model features to individual predictions.",
            "Positive SHAP values support the predicted class.",
            "Negative SHAP values push the prediction away from the predicted class.",
            "Feature importance represents learned statistical associations, not factual causation.",
            "TF-IDF terms and engineered linguistic features are both included in the explanation.",
            "The explanations describe model behavior and should not be interpreted as evidence that a specific word causes a claim to be true or false.",
        ],
    }

    # --------------------------------------------------------
    # Save artifact
    # --------------------------------------------------------

    print("\n[7/7] Saving SHAP artifact...")

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

    # --------------------------------------------------------
    # Console summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TOP SHAP FEATURES BY CLASS")
    print("=" * 70)

    for class_label, explanation_data in (
        global_explanations.items()
    ):

        print(
            f"\nClass {class_label}"
        )

        for feature in explanation_data[
            "top_features"
        ][:10]:

            print(
                f"  {feature['feature']:<30} "
                f"| mean |SHAP| = "
                f"{feature['mean_absolute_shap']:.6f} "
                f"| mean SHAP = "
                f"{feature['mean_shap']:+.6f}"
            )

    print("\n" + "=" * 70)
    print("SHAP TEXT EXPLAINABILITY COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()