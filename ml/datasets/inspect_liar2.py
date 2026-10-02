from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# VeriLens — LIAR2 Dataset Inspection
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = PROJECT_ROOT / "data" / "raw" / "liar2"


def inspect_split(split_name: str) -> pd.DataFrame:
    file_path = DATASET_DIR / f"{split_name}.csv"

    print()
    print("=" * 70)
    print(f"📊 {split_name.upper()} SPLIT")
    print("=" * 70)

    dataframe = pd.read_csv(file_path)

    print()
    print(f"Rows:    {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns)}")

    print()
    print("Columns:")
    for column in dataframe.columns:
        print(f"   • {column}")

    print()
    print("Missing values:")
    missing = dataframe.isna().sum()

    missing_found = False

    for column, count in missing.items():
        if count > 0:
            missing_found = True
            percentage = (count / len(dataframe)) * 100
            print(
                f"   • {column}: "
                f"{count:,} ({percentage:.2f}%)"
            )

    if not missing_found:
        print("   ✅ No missing values")

    print()
    print("Duplicate rows:")
    duplicates = dataframe.duplicated().sum()
    print(f"   {duplicates:,}")

    if duplicates == 0:
        print("   ✅ No duplicate rows")
    else:
        print("   ⚠️ Duplicate rows detected")

    print()
    print("Statement statistics:")

    if "statement" in dataframe.columns:
        statement_lengths = (
            dataframe["statement"]
            .fillna("")
            .astype(str)
            .str.len()
        )

        print(
            f"   Average length: {statement_lengths.mean():.1f} characters"
        )
        print(
            f"   Minimum length: {statement_lengths.min():,} characters"
        )
        print(
            f"   Maximum length: {statement_lengths.max():,} characters"
        )

        empty_statements = (
            dataframe["statement"]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        print(f"   Empty statements: {empty_statements:,}")

    print()
    print("Label distribution:")

    if "label" in dataframe.columns:
        label_counts = dataframe["label"].value_counts().sort_index()

        for label, count in label_counts.items():
            percentage = (count / len(dataframe)) * 100

            print(
                f"   Label {label}: "
                f"{count:,} "
                f"({percentage:.2f}%)"
            )

    print()

    return dataframe


def compare_columns(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> None:

    print("=" * 70)
    print("🔎 SPLIT CONSISTENCY CHECK")
    print("=" * 70)

    train_columns = list(train_df.columns)
    validation_columns = list(validation_df.columns)
    test_columns = list(test_df.columns)

    print()

    if (
        train_columns
        == validation_columns
        == test_columns
    ):
        print("✅ All splits contain the same columns.")
    else:
        print("⚠️ Column mismatch detected.")

    print()
    print("Column count:")
    print(f"   Train:      {len(train_columns)}")
    print(f"   Validation: {len(validation_columns)}")
    print(f"   Test:       {len(test_columns)}")


def check_statement_overlap(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> None:

    print()
    print("=" * 70)
    print("🔐 POTENTIAL TEXT LEAKAGE CHECK")
    print("=" * 70)

    if "statement" not in train_df.columns:
        print()
        print("⚠️ Statement column not found.")
        return

    train_statements = set(
        train_df["statement"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    validation_statements = set(
        validation_df["statement"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    test_statements = set(
        test_df["statement"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    train_validation_overlap = (
        train_statements & validation_statements
    )

    train_test_overlap = (
        train_statements & test_statements
    )

    validation_test_overlap = (
        validation_statements & test_statements
    )

    print()
    print(
        f"Train ↔ Validation overlap: "
        f"{len(train_validation_overlap):,}"
    )

    print(
        f"Train ↔ Test overlap:       "
        f"{len(train_test_overlap):,}"
    )

    print(
        f"Validation ↔ Test overlap:   "
        f"{len(validation_test_overlap):,}"
    )

    if (
        len(train_validation_overlap) == 0
        and len(train_test_overlap) == 0
        and len(validation_test_overlap) == 0
    ):
        print()
        print("✅ No exact statement overlap detected.")
    else:
        print()
        print(
            "⚠️ Exact statement overlap detected."
        )


def main() -> None:

    print("=" * 70)
    print("🧿 VeriLens — LIAR2 Dataset Inspection")
    print("=" * 70)

    print()
    print(f"📁 Dataset directory:")
    print(f"   {DATASET_DIR}")

    train_df = inspect_split("train")
    validation_df = inspect_split("validation")
    test_df = inspect_split("test")

    print()
    compare_columns(
        train_df,
        validation_df,
        test_df,
    )

    check_statement_overlap(
        train_df,
        validation_df,
        test_df,
    )

    print()
    print("=" * 70)
    print("✅ DATASET INSPECTION COMPLETE")
    print("=" * 70)

    print()
    print("Next step:")
    print("Review the inspection results before preprocessing.")


if __name__ == "__main__":
    main()