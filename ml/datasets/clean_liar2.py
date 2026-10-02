from pathlib import Path
import json

import pandas as pd


# ---------------------------------------------------------
# VeriLens — LIAR2 Cleaning & Leakage-Safe Dataset Builder
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "liar2"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "liar2"


SPLITS = [
    "train",
    "validation",
    "test",
]


def normalize_statement(value: str) -> str:
    """
    Normalize statement text only for duplicate/leakage detection.

    The original statement is preserved.
    """

    return (
        str(value)
        .strip()
        .lower()
        .replace("\n", " ")
        .replace("\r", " ")
    )


def load_data() -> dict[str, pd.DataFrame]:
    """Load the original raw dataset."""

    datasets = {}

    for split in SPLITS:
        path = RAW_DIR / f"{split}.csv"

        if not path.exists():
            raise FileNotFoundError(
                f"Missing dataset file: {path}"
            )

        datasets[split] = pd.read_csv(path)

    return datasets


def analyze_duplicates(
    datasets: dict[str, pd.DataFrame],
) -> dict:
    """
    Analyze duplicate statements within and across splits.
    """

    report = {
        "within_split": {},
        "cross_split": {},
        "conflicting_labels": [],
    }

    normalized_sets = {}

    print()
    print("=" * 70)
    print("🔎 DUPLICATE STATEMENT ANALYSIS")
    print("=" * 70)

    # -----------------------------------------------------
    # Within-split duplicates
    # -----------------------------------------------------

    for split, dataframe in datasets.items():

        normalized = (
            dataframe["statement"]
            .fillna("")
            .map(normalize_statement)
        )

        duplicate_count = int(
            normalized.duplicated(keep=False).sum()
        )

        unique_duplicate_statements = int(
            normalized[normalized.duplicated(keep=False)]
            .nunique()
        )

        report["within_split"][split] = {
            "duplicate_rows": duplicate_count,
            "duplicate_statement_groups": unique_duplicate_statements,
        }

        normalized_sets[split] = normalized

        print()
        print(f"{split.upper()}:")
        print(
            f"   Duplicate rows: "
            f"{duplicate_count:,}"
        )
        print(
            f"   Duplicate statement groups: "
            f"{unique_duplicate_statements:,}"
        )

    # -----------------------------------------------------
    # Cross-split duplicates
    # -----------------------------------------------------

    print()
    print("Cross-split duplicates:")

    split_pairs = [
        ("train", "validation"),
        ("train", "test"),
        ("validation", "test"),
    ]

    for first_split, second_split in split_pairs:

        first_set = set(
            normalized_sets[first_split]
        )

        second_set = set(
            normalized_sets[second_split]
        )

        overlap = (
            first_set & second_set
        )

        report["cross_split"][
            f"{first_split}_vs_{second_split}"
        ] = len(overlap)

        print(
            f"   {first_split} ↔ {second_split}: "
            f"{len(overlap):,}"
        )

    # -----------------------------------------------------
    # Conflicting labels
    # -----------------------------------------------------

    print()
    print("Checking conflicting labels...")

    combined_records = []

    for split, dataframe in datasets.items():

        for _, row in dataframe.iterrows():

            combined_records.append(
                {
                    "split": split,
                    "id": row["id"],
                    "statement": row["statement"],
                    "normalized_statement": normalize_statement(
                        row["statement"]
                    ),
                    "label": row["label"],
                }
            )

    combined = pd.DataFrame(combined_records)

    grouped = combined.groupby(
        "normalized_statement"
    )

    for statement, group in grouped:

        unique_labels = (
            group["label"]
            .dropna()
            .unique()
            .tolist()
        )

        if len(unique_labels) > 1:

            record = {
                "statement": statement,
                "labels": sorted(
                    int(label)
                    for label in unique_labels
                ),
                "records": group[
                    [
                        "split",
                        "id",
                        "label",
                    ]
                ].to_dict(
                    orient="records"
                ),
            }

            report[
                "conflicting_labels"
            ].append(record)

    print(
        f"   Conflicting statement groups: "
        f"{len(report['conflicting_labels']):,}"
    )

    return report


def create_clean_splits(
    datasets: dict[str, pd.DataFrame],
) -> tuple[dict[str, pd.DataFrame], dict]:
    """
    Create leakage-safe experimental splits.

    Policy:
    - Raw data is never modified.
    - Any statement appearing in more than one split
      is removed from ALL processed splits.
    - This prevents the same text from appearing in
      train/validation/test.
    - Conflicting-label records are therefore also removed.
    """

    print()
    print("=" * 70)
    print("🧹 BUILDING LEAKAGE-SAFE DATASET")
    print("=" * 70)

    normalized_sets = {}

    for split, dataframe in datasets.items():

        normalized_sets[split] = set(
            dataframe["statement"]
            .fillna("")
            .map(normalize_statement)
        )

    all_sets = list(normalized_sets.values())

    duplicated_across_splits = set()

    for index, first_set in enumerate(all_sets):

        for second_set in all_sets[index + 1:]:

            duplicated_across_splits.update(
                first_set & second_set
            )

    print()
    print(
        f"🚨 Statements appearing across splits: "
        f"{len(duplicated_across_splits):,}"
    )

    cleaned = {}

    removal_report = {}

    for split, dataframe in datasets.items():

        dataframe = dataframe.copy()

        dataframe[
            "_normalized_statement"
        ] = (
            dataframe["statement"]
            .fillna("")
            .map(normalize_statement)
        )

        before = len(dataframe)

        dataframe = dataframe[
            ~dataframe[
                "_normalized_statement"
            ].isin(
                duplicated_across_splits
            )
        ].copy()

        dataframe.drop(
            columns=[
                "_normalized_statement"
            ],
            inplace=True,
        )

        after = len(dataframe)

        removed = before - after

        cleaned[split] = dataframe

        removal_report[split] = {
            "before": before,
            "after": after,
            "removed": removed,
        }

        print()
        print(f"{split.upper()}:")
        print(f"   Before: {before:,}")
        print(f"   Removed: {removed:,}")
        print(f"   After: {after:,}")

    return cleaned, removal_report


def save_processed_data(
    cleaned: dict[str, pd.DataFrame],
    analysis_report: dict,
    removal_report: dict,
) -> None:

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("=" * 70)
    print("💾 SAVING PROCESSED DATA")
    print("=" * 70)

    for split, dataframe in cleaned.items():

        output_file = (
            PROCESSED_DIR
            / f"{split}.csv"
        )

        dataframe.to_csv(
            output_file,
            index=False,
            encoding="utf-8",
        )

        print()
        print(
            f"✅ {split}.csv "
            f"({len(dataframe):,} rows)"
        )

    report = {
        "dataset": "chengxuphd/liar2",
        "processing_policy": {
            "raw_data_modified": False,
            "cross_split_duplicate_policy": (
                "Remove statements appearing "
                "in more than one split from "
                "all processed splits."
            ),
            "original_statements_preserved": True,
        },
        "duplicate_analysis": analysis_report,
        "removal_report": removal_report,
    }

    report_file = (
        PROCESSED_DIR
        / "cleaning_report.json"
    )

    with report_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"📄 Cleaning report saved:"
    )
    print(
        f"   {report_file}"
    )


def main() -> None:

    print("=" * 70)
    print("🧿 VeriLens — LIAR2 Cleaning Pipeline")
    print("=" * 70)

    print()
    print(
        "📁 Raw dataset:"
    )
    print(
        f"   {RAW_DIR}"
    )

    print()
    print(
        "📁 Processed dataset:"
    )
    print(
        f"   {PROCESSED_DIR}"
    )

    datasets = load_data()

    analysis_report = analyze_duplicates(
        datasets
    )

    cleaned, removal_report = (
        create_clean_splits(
            datasets
        )
    )

    save_processed_data(
        cleaned,
        analysis_report,
        removal_report,
    )

    print()
    print("=" * 70)
    print("✅ CLEANING PIPELINE COMPLETE")
    print("=" * 70)

    print()
    print("Created:")
    print(
        "   • data/processed/liar2/train.csv"
    )
    print(
        "   • data/processed/liar2/validation.csv"
    )
    print(
        "   • data/processed/liar2/test.csv"
    )
    print(
        "   • data/processed/liar2/cleaning_report.json"
    )

    print()
    print(
        "Next step: "
        "build the preprocessing + feature engineering pipeline."
    )


if __name__ == "__main__":
    main()