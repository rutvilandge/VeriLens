from pathlib import Path
import json
import re

import pandas as pd


# ---------------------------------------------------------
# VeriLens — Text Preprocessing & Feature Engineering
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "processed" / "liar2"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "liar2_features"


SPLITS = [
    "train",
    "validation",
    "test",
]


def clean_text(text: str) -> str:
    """
    Basic text normalization.

    Important:
    We intentionally keep the transformation conservative.
    Transformer models will later receive richer text.
    """

    text = str(text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    # Lowercase for classical NLP features
    text = text.lower()

    return text


def calculate_text_features(text: str) -> dict:
    """
    Extract lightweight linguistic/statistical features.
    """

    text = str(text)

    words = re.findall(
        r"\b\w+\b",
        text,
    )

    sentences = re.split(
        r"[.!?]+",
        text,
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    characters = len(text)

    word_count = len(words)

    sentence_count = len(sentences)

    if word_count > 0:
        average_word_length = (
            sum(len(word) for word in words)
            / word_count
        )
    else:
        average_word_length = 0.0

    uppercase_letters = sum(
        1
        for character in text
        if character.isupper()
    )

    alphabetic_characters = sum(
        1
        for character in text
        if character.isalpha()
    )

    if alphabetic_characters > 0:
        uppercase_ratio = (
            uppercase_letters
            / alphabetic_characters
        )
    else:
        uppercase_ratio = 0.0

    punctuation_count = sum(
        1
        for character in text
        if character in ".,!?;:"
    )

    question_mark_count = text.count("?")

    exclamation_mark_count = text.count("!")

    return {
        "character_count": characters,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "average_word_length": round(
            average_word_length,
            4,
        ),
        "uppercase_ratio": round(
            uppercase_ratio,
            4,
        ),
        "punctuation_count": punctuation_count,
        "question_mark_count": question_mark_count,
        "exclamation_mark_count": exclamation_mark_count,
    }


def preprocess_split(
    split_name: str,
) -> tuple[pd.DataFrame, dict]:

    input_file = (
        INPUT_DIR
        / f"{split_name}.csv"
    )

    dataframe = pd.read_csv(input_file)

    original_rows = len(dataframe)

    # -----------------------------------------------------
    # Preserve original statement
    # -----------------------------------------------------

    dataframe["statement_original"] = (
        dataframe["statement"]
        .fillna("")
        .astype(str)
    )

    # -----------------------------------------------------
    # Clean text
    # -----------------------------------------------------

    dataframe["statement_clean"] = (
        dataframe["statement_original"]
        .map(clean_text)
    )

    # -----------------------------------------------------
    # Extract text features
    # -----------------------------------------------------

    feature_records = (
        dataframe["statement_original"]
        .map(calculate_text_features)
        .tolist()
    )

    feature_dataframe = pd.DataFrame(
        feature_records
    )

    dataframe = pd.concat(
        [
            dataframe,
            feature_dataframe,
        ],
        axis=1,
    )

    # -----------------------------------------------------
    # Check empty cleaned statements
    # -----------------------------------------------------

    empty_cleaned = int(
        dataframe["statement_clean"]
        .str.strip()
        .eq("")
        .sum()
    )

    # -----------------------------------------------------
    # Remove only rows with unusable text
    # -----------------------------------------------------

    if empty_cleaned > 0:

        dataframe = dataframe[
            dataframe["statement_clean"]
            .str.strip()
            .ne("")
        ].copy()

    report = {
        "split": split_name,
        "original_rows": original_rows,
        "final_rows": len(dataframe),
        "removed_empty_text": empty_cleaned,
        "columns_added": [
            "statement_original",
            "statement_clean",
            "character_count",
            "word_count",
            "sentence_count",
            "average_word_length",
            "uppercase_ratio",
            "punctuation_count",
            "question_mark_count",
            "exclamation_mark_count",
        ],
    }

    return dataframe, report


def main() -> None:

    print("=" * 70)
    print("🧿 VeriLens — Text Preprocessing")
    print("=" * 70)

    print()
    print(f"📁 Input:")
    print(f"   {INPUT_DIR}")

    print()
    print(f"📁 Output:")
    print(f"   {OUTPUT_DIR}")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    reports = {}

    for split in SPLITS:

        print()
        print("=" * 70)
        print(f"📝 PROCESSING: {split.upper()}")
        print("=" * 70)

        dataframe, report = preprocess_split(
            split
        )

        output_file = (
            OUTPUT_DIR
            / f"{split}.csv"
        )

        dataframe.to_csv(
            output_file,
            index=False,
            encoding="utf-8",
        )

        reports[split] = report

        print()
        print(
            f"Original rows: "
            f"{report['original_rows']:,}"
        )

        print(
            f"Final rows:    "
            f"{report['final_rows']:,}"
        )

        print(
            f"Empty text removed: "
            f"{report['removed_empty_text']:,}"
        )

        print(
            f"Saved: {output_file}"
        )

    # -----------------------------------------------------
    # Save preprocessing report
    # -----------------------------------------------------

    report_file = (
        OUTPUT_DIR
        / "preprocessing_report.json"
    )

    with report_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "dataset": "chengxuphd/liar2",
                "description": (
                    "Text normalization and "
                    "statistical feature engineering"
                ),
                "reports": reports,
            },
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 70)
    print("✅ TEXT PREPROCESSING COMPLETE")
    print("=" * 70)

    print()
    print("Created:")

    for split in SPLITS:
        print(
            f"   • "
            f"data/processed/liar2_features/{split}.csv"
        )

    print(
        "   • "
        "data/processed/liar2_features/preprocessing_report.json"
    )

    print()
    print(
        "Next step: "
        "TF-IDF feature extraction."
    )


if __name__ == "__main__":
    main()