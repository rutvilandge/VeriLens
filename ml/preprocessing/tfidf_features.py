from pathlib import Path
import json

import joblib
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


# ---------------------------------------------------------
# VeriLens — TF-IDF Feature Extraction
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "processed" / "liar2_features"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "tfidf"

SPLITS = [
    "train",
    "validation",
    "test",
]

TEXT_COLUMN = "statement_clean"

# Keep this moderate for a strong CPU-friendly baseline.
MAX_FEATURES = 15000

NGRAM_RANGE = (1, 2)

MIN_DF = 2

MAX_DF = 0.95


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

def load_split(split_name: str) -> pd.DataFrame:
    file_path = INPUT_DIR / f"{split_name}.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing file: {file_path}"
        )

    dataframe = pd.read_csv(file_path)

    if TEXT_COLUMN not in dataframe.columns:
        raise ValueError(
            f"Missing required column: {TEXT_COLUMN}"
        )

    return dataframe


# ---------------------------------------------------------
# Select numerical engineered features
# ---------------------------------------------------------

def get_numeric_features(
    dataframe: pd.DataFrame,
) -> csr_matrix:

    feature_columns = [
        "character_count",
        "word_count",
        "sentence_count",
        "average_word_length",
        "uppercase_ratio",
        "punctuation_count",
        "question_mark_count",
        "exclamation_mark_count",
    ]

    missing = [
        column
        for column in feature_columns
        if column not in dataframe.columns
    ]

    if missing:
        raise ValueError(
            "Missing engineered feature columns: "
            + ", ".join(missing)
        )

    numeric = dataframe[
        feature_columns
    ].fillna(0)

    return csr_matrix(
        numeric.astype(float).values
    )


# ---------------------------------------------------------
# Save sparse matrix
# ---------------------------------------------------------

def save_matrix(
    matrix,
    labels,
    split_name: str,
) -> None:

    matrix_file = (
        OUTPUT_DIR
        / f"{split_name}_features.npz"
    )

    labels_file = (
        OUTPUT_DIR
        / f"{split_name}_labels.csv"
    )

    from scipy.sparse import save_npz

    save_npz(
        matrix_file,
        matrix,
    )

    pd.DataFrame(
        {
            "label": labels,
        }
    ).to_csv(
        labels_file,
        index=False,
    )

    print(
        f"   ✅ Features: {matrix_file}"
    )

    print(
        f"   ✅ Labels:   {labels_file}"
    )


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def main() -> None:

    print("=" * 70)
    print("🧿 VeriLens — TF-IDF Feature Extraction")
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("📥 Loading processed datasets...")

    train_df = load_split("train")
    validation_df = load_split("validation")
    test_df = load_split("test")

    print(
        f"   Train:      {len(train_df):,}"
    )

    print(
        f"   Validation: {len(validation_df):,}"
    )

    print(
        f"   Test:       {len(test_df):,}"
    )

    # -----------------------------------------------------
    # TF-IDF
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("🔤 FITTING TF-IDF")
    print("=" * 70)

    print()
    print("Configuration:")
    print(f"   Max features: {MAX_FEATURES:,}")
    print(f"   N-grams:      {NGRAM_RANGE}")
    print(f"   Min DF:       {MIN_DF}")
    print(f"   Max DF:       {MAX_DF}")

    print()
    print(
        "⚠️ TF-IDF is fitted ONLY on training text."
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=NGRAM_RANGE,
        max_features=MAX_FEATURES,
        min_df=MIN_DF,
        max_df=MAX_DF,
        sublinear_tf=True,
    )

    X_train_text = vectorizer.fit_transform(
        train_df[TEXT_COLUMN]
    )

    X_validation_text = vectorizer.transform(
        validation_df[TEXT_COLUMN]
    )

    X_test_text = vectorizer.transform(
        test_df[TEXT_COLUMN]
    )

    print()
    print("Vocabulary size:")
    print(
        f"   {len(vectorizer.vocabulary_):,}"
    )

    print()
    print("TF-IDF matrix shapes:")

    print(
        f"   Train:      {X_train_text.shape}"
    )

    print(
        f"   Validation: {X_validation_text.shape}"
    )

    print(
        f"   Test:       {X_test_text.shape}"
    )

    # -----------------------------------------------------
    # Engineered numerical features
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("📊 ADDING ENGINEERED FEATURES")
    print("=" * 70)

    X_train_numeric = get_numeric_features(
        train_df
    )

    X_validation_numeric = get_numeric_features(
        validation_df
    )

    X_test_numeric = get_numeric_features(
        test_df
    )

    print()
    print(
        f"   Numerical features: "
        f"{X_train_numeric.shape[1]}"
    )

    # -----------------------------------------------------
    # Combine features
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("🔗 COMBINING FEATURES")
    print("=" * 70)

    X_train = hstack(
        [
            X_train_text,
            X_train_numeric,
        ],
        format="csr",
    )

    X_validation = hstack(
        [
            X_validation_text,
            X_validation_numeric,
        ],
        format="csr",
    )

    X_test = hstack(
        [
            X_test_text,
            X_test_numeric,
        ],
        format="csr",
    )

    print()
    print("Combined feature shapes:")

    print(
        f"   Train:      {X_train.shape}"
    )

    print(
        f"   Validation: {X_validation.shape}"
    )

    print(
        f"   Test:       {X_test.shape}"
    )

    # -----------------------------------------------------
    # Labels
    # -----------------------------------------------------

    y_train = train_df["label"].values
    y_validation = validation_df["label"].values
    y_test = test_df["label"].values

    # -----------------------------------------------------
    # Save feature matrices
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("💾 SAVING FEATURE MATRICES")
    print("=" * 70)

    save_matrix(
        X_train,
        y_train,
        "train",
    )

    save_matrix(
        X_validation,
        y_validation,
        "validation",
    )

    save_matrix(
        X_test,
        y_test,
        "test",
    )

    # -----------------------------------------------------
    # Save vectorizer
    # -----------------------------------------------------

    vectorizer_file = (
        OUTPUT_DIR
        / "tfidf_vectorizer.joblib"
    )

    joblib.dump(
        vectorizer,
        vectorizer_file,
    )

    print()
    print(
        f"   ✅ Vectorizer: "
        f"{vectorizer_file}"
    )

    # -----------------------------------------------------
    # Save feature metadata
    # -----------------------------------------------------

    metadata = {
        "dataset": "chengxuphd/liar2",
        "text_column": TEXT_COLUMN,
        "max_features": MAX_FEATURES,
        "ngram_range": list(NGRAM_RANGE),
        "min_df": MIN_DF,
        "max_df": MAX_DF,
        "sublinear_tf": True,
        "tfidf_vocabulary_size": len(
            vectorizer.vocabulary_
        ),
        "engineered_features": [
            "character_count",
            "word_count",
            "sentence_count",
            "average_word_length",
            "uppercase_ratio",
            "punctuation_count",
            "question_mark_count",
            "exclamation_mark_count",
        ],
        "total_features": int(
            X_train.shape[1]
        ),
        "train_rows": int(
            X_train.shape[0]
        ),
        "validation_rows": int(
            X_validation.shape[0]
        ),
        "test_rows": int(
            X_test.shape[0]
        ),
        "fit_policy": (
            "TF-IDF vocabulary fitted only "
            "on training data; validation "
            "and test data transformed using "
            "the training vocabulary."
        ),
    }

    metadata_file = (
        OUTPUT_DIR
        / "feature_metadata.json"
    )

    with metadata_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"   ✅ Metadata: "
        f"{metadata_file}"
    )

    print()
    print("=" * 70)
    print("✅ TF-IDF FEATURE EXTRACTION COMPLETE")
    print("=" * 70)

    print()
    print("Created:")
    print(
        "   • train_features.npz"
    )
    print(
        "   • validation_features.npz"
    )
    print(
        "   • test_features.npz"
    )
    print(
        "   • train_labels.csv"
    )
    print(
        "   • validation_labels.csv"
    )
    print(
        "   • test_labels.csv"
    )
    print(
        "   • tfidf_vectorizer.joblib"
    )
    print(
        "   • feature_metadata.json"
    )

    print()
    print(
        "🚀 Next: Classical ML baseline."
    )


if __name__ == "__main__":
    main()