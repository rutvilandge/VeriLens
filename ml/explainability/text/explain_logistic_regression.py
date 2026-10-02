
from pathlib import Path
import json

import joblib
import numpy as np
from scipy.sparse import load_npz


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = Path(
    "ml/models/classical_ml/saved/logistic_regression_v2.joblib"
)

VECTORIZER_PATH = Path(
    "data/processed/tfidf/tfidf_vectorizer.joblib"
)

TEST_FEATURES_PATH = Path(
    "data/processed/tfidf/test_features.npz"
)

OUTPUT_DIR = Path(
    "ml/explainability/artifacts"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TOP_N = 20


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    """Load the trained Logistic Regression v2 model."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found:\n{MODEL_PATH}"
        )

    model = joblib.load(
        MODEL_PATH
    )

    print(
        f"Loaded model: {MODEL_PATH}"
    )

    return model


# ============================================================
# LOAD VECTORIZER
# ============================================================

def load_vectorizer():
    """Load the Phase 1 TF-IDF vectorizer."""

    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            f"TF-IDF vectorizer not found:\n"
            f"{VECTORIZER_PATH}"
        )

    vectorizer = joblib.load(
        VECTORIZER_PATH
    )

    print(
        f"Loaded vectorizer: {VECTORIZER_PATH}"
    )

    return vectorizer


# ============================================================
# FEATURE NAMES
# ============================================================

def build_feature_names(vectorizer):
    """
    Phase 1 feature structure:

        15,000 TF-IDF features
        +
        8 engineered numerical features

        = 15,008 total features
    """

    try:
        tfidf_features = (
            vectorizer.get_feature_names_out()
        )

    except AttributeError:
        tfidf_features = (
            vectorizer.get_feature_names()
        )

    tfidf_features = np.asarray(
        tfidf_features
    )

    engineered_features = np.array(
        [
            "char_count",
            "word_count",
            "sentence_count",
            "average_word_length",
            "uppercase_ratio",
            "punctuation_count",
            "question_mark_count",
            "exclamation_mark_count",
        ]
    )

    feature_names = np.concatenate(
        [
            tfidf_features,
            engineered_features,
        ]
    )

    return feature_names


# ============================================================
# LOAD TEST FEATURES
# ============================================================

def load_test_features():
    """
    Load the sparse TF-IDF + engineered feature matrix.

    Phase 1 saved this using scipy.sparse.save_npz(),
    so scipy.sparse.load_npz() must be used here.
    """

    if not TEST_FEATURES_PATH.exists():
        raise FileNotFoundError(
            "Test feature matrix not found:\n"
            f"{TEST_FEATURES_PATH}"
        )

    print()
    print(
        "Loading sparse TF-IDF test matrix..."
    )

    X_test = load_npz(
        TEST_FEATURES_PATH
    )

    print(
        f"Test matrix shape: {X_test.shape}"
    )

    print(
        f"Test matrix type: "
        f"{type(X_test).__name__}"
    )

    return X_test


# ============================================================
# GLOBAL FEATURE IMPORTANCE
# ============================================================

def calculate_global_importance(
    model,
    feature_names
):
    """
    Calculate global feature importance using
    Logistic Regression coefficients.

    For each class:

        positive coefficient
        = pushes prediction toward that class

        negative coefficient
        = pushes prediction away from that class
    """

    coefficients = model.coef_

    classes = model.classes_

    print()
    print(
        "=" * 80
    )
    print(
        "GLOBAL FEATURE IMPORTANCE"
    )
    print(
        "=" * 80
    )

    print(
        f"Number of classes : {len(classes)}"
    )

    print(
        f"Number of features: "
        f"{len(feature_names)}"
    )

    results = []

    for class_index, class_label in enumerate(
        classes
    ):

        class_coefficients = coefficients[
            class_index
        ]

        # Largest positive coefficients
        top_positive_indices = np.argsort(
            class_coefficients
        )[-TOP_N:][::-1]

        # Largest negative coefficients
        top_negative_indices = np.argsort(
            class_coefficients
        )[:TOP_N]

        positive_features = []

        for index in top_positive_indices:

            positive_features.append(
                {
                    "feature": str(
                        feature_names[index]
                    ),
                    "coefficient": float(
                        class_coefficients[index]
                    )
                }
            )

        negative_features = []

        for index in top_negative_indices:

            negative_features.append(
                {
                    "feature": str(
                        feature_names[index]
                    ),
                    "coefficient": float(
                        class_coefficients[index]
                    )
                }
            )

        results.append(
            {
                "class": int(
                    class_label
                ),
                "top_positive_features":
                    positive_features,
                "top_negative_features":
                    negative_features,
            }
        )

    return results


# ============================================================
# SAMPLE-LEVEL EXPLANATION
# ============================================================

def explain_sample(
    model,
    feature_names,
    X,
    sample_index
):
    """
    Explain one prediction using:

        feature_value × model_coefficient

    This gives a local contribution score for
    each active feature.
    """

    sample = X[
        sample_index
    ]

    prediction = model.predict(
        sample
    )[0]

    probabilities = model.predict_proba(
        sample
    )[0]

    class_index = list(
        model.classes_
    ).index(
        prediction
    )

    coefficients = model.coef_[
        class_index
    ]

    # Convert only this single sparse row
    # to dense representation.
    sample_values = (
        sample.toarray()[0]
    )

    contributions = (
        sample_values * coefficients
    )

    # --------------------------------------------------------
    # Positive contributions
    # --------------------------------------------------------

    positive_indices = np.argsort(
        contributions
    )[-TOP_N:][::-1]

    positive = []

    for index in positive_indices:

        if sample_values[index] == 0:
            continue

        positive.append(
            {
                "feature": str(
                    feature_names[index]
                ),
                "feature_value": float(
                    sample_values[index]
                ),
                "coefficient": float(
                    coefficients[index]
                ),
                "contribution": float(
                    contributions[index]
                ),
            }
        )

    # --------------------------------------------------------
    # Negative contributions
    # --------------------------------------------------------

    negative_indices = np.argsort(
        contributions
    )[:TOP_N]

    negative = []

    for index in negative_indices:

        if sample_values[index] == 0:
            continue

        negative.append(
            {
                "feature": str(
                    feature_names[index]
                ),
                "feature_value": float(
                    sample_values[index]
                ),
                "coefficient": float(
                    coefficients[index]
                ),
                "contribution": float(
                    contributions[index]
                ),
            }
        )

    return {
        "sample_index": int(
            sample_index
        ),
        "predicted_class": int(
            prediction
        ),
        "probabilities": {
            str(label): float(
                probability
            )
            for label, probability
            in zip(
                model.classes_,
                probabilities
            )
        },
        "top_positive_contributions":
            positive,
        "top_negative_contributions":
            negative,
    }


# ============================================================
# PRINT GLOBAL RESULTS
# ============================================================

def print_global_results(
    global_results
):

    for class_result in global_results:

        print()
        print(
            "-" * 80
        )

        print(
            f"CLASS "
            f"{class_result['class']}"
        )

        print()
        print(
            "Top positive features:"
        )

        for item in class_result[
            "top_positive_features"
        ][:10]:

            print(
                f"  "
                f"{item['feature']:<35}"
                f"{item['coefficient']:+.6f}"
            )

        print()
        print(
            "Top negative features:"
        )

        for item in class_result[
            "top_negative_features"
        ][:10]:

            print(
                f"  "
                f"{item['feature']:<35}"
                f"{item['coefficient']:+.6f}"
            )


# ============================================================
# PRINT LOCAL RESULTS
# ============================================================

def print_local_explanation(
    explanation
):

    print()
    print(
        "-" * 80
    )

    print(
        f"Sample "
        f"{explanation['sample_index']}"
    )

    print(
        f"Predicted class: "
        f"{explanation['predicted_class']}"
    )

    print()
    print(
        "Class probabilities:"
    )

    for label, probability in (
        explanation["probabilities"]
        .items()
    ):

        print(
            f"  Class {label}: "
            f"{probability:.4f}"
        )

    print()
    print(
        "Top positive contributions:"
    )

    for item in explanation[
        "top_positive_contributions"
    ][:5]:

        print(
            f"  "
            f"{item['feature']:<30}"
            f"{item['contribution']:+.6f}"
        )

    print()
    print(
        "Top negative contributions:"
    )

    for item in explanation[
        "top_negative_contributions"
    ][:5]:

        print(
            f"  "
            f"{item['feature']:<30}"
            f"{item['contribution']:+.6f}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 80
    )

    print(
        "VERILENS PHASE 6 — EXPLAINABLE AI"
    )

    print(
        "LOGISTIC REGRESSION FEATURE EXPLANATION"
    )

    print(
        "=" * 80
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # Load vectorizer
    # --------------------------------------------------------

    vectorizer = load_vectorizer()

    # --------------------------------------------------------
    # Build complete feature names
    # --------------------------------------------------------

    feature_names = build_feature_names(
        vectorizer
    )

    print()
    print(
        f"TF-IDF features: "
        f"{len(vectorizer.get_feature_names_out())}"
    )

    print(
        f"Total explanation features: "
        f"{len(feature_names)}"
    )

    # --------------------------------------------------------
    # Load sparse test matrix
    # --------------------------------------------------------

    X_test = load_test_features()

    # --------------------------------------------------------
    # Validate dimensions
    # --------------------------------------------------------

    expected_features = len(
        feature_names
    )

    actual_features = X_test.shape[1]

    print()
    print(
        "=" * 80
    )

    print(
        "FEATURE DIMENSION CHECK"
    )

    print(
        "=" * 80
    )

    print(
        f"Explanation feature names: "
        f"{expected_features}"
    )

    print(
        f"Test matrix features: "
        f"{actual_features}"
    )

    print(
        f"Model features: "
        f"{model.coef_.shape[1]}"
    )

    if (
        expected_features
        != actual_features
        or
        actual_features
        != model.coef_.shape[1]
    ):

        raise ValueError(
            "\nFeature dimension mismatch.\n"
            f"Explanation names: "
            f"{expected_features}\n"
            f"Test matrix: "
            f"{actual_features}\n"
            f"Model: "
            f"{model.coef_.shape[1]}"
        )

    print(
        "STATUS: Feature dimensions match."
    )

    # --------------------------------------------------------
    # Global explanation
    # --------------------------------------------------------

    global_results = (
        calculate_global_importance(
            model,
            feature_names
        )
    )

    print_global_results(
        global_results
    )

    # --------------------------------------------------------
    # Local explanations
    # --------------------------------------------------------

    sample_indices = [
        0,
        min(
            10,
            X_test.shape[0] - 1
        ),
        min(
            100,
            X_test.shape[0] - 1
        ),
    ]

    local_results = []

    print()
    print(
        "=" * 80
    )

    print(
        "LOCAL SAMPLE EXPLANATIONS"
    )

    print(
        "=" * 80
    )

    for sample_index in (
        sample_indices
    ):

        explanation = explain_sample(
            model,
            feature_names,
            X_test,
            sample_index
        )

        local_results.append(
            explanation
        )

        print_local_explanation(
            explanation
        )

    # --------------------------------------------------------
    # Save explanation artifact
    # --------------------------------------------------------

    output = {
        "phase":
            "Phase 6 — Explainable AI",

        "model":
            "Logistic Regression v2",

        "dataset":
            "LIAR-2",

        "explanation_method":
            "TF-IDF feature value × "
            "Logistic Regression coefficient",

        "feature_count":
            int(
                len(feature_names)
            ),

        "test_samples_explained":
            sample_indices,

        "global_feature_importance":
            global_results,

        "local_sample_explanations":
            local_results,
    }

    output_path = (
        OUTPUT_DIR
        /
        "logistic_regression_explanations.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2
        )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print(
        "=" * 80
    )

    print(
        "EXPLAINABILITY ANALYSIS COMPLETE"
    )

    print(
        "=" * 80
    )

    print(
        f"Saved explanation artifact:"
    )

    print(
        output_path
    )


if __name__ == "__main__":
    main()