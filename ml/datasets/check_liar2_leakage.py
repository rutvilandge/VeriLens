from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# VeriLens — LIAR2 Leakage Investigation
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = PROJECT_ROOT / "data" / "raw" / "liar2"


def load_split(name: str) -> pd.DataFrame:
    return pd.read_csv(DATASET_DIR / f"{name}.csv")


def normalize_statement(value: str) -> str:
    return (
        str(value)
        .strip()
        .lower()
        .replace("\n", " ")
    )


def find_overlap(
    first_name: str,
    first_df: pd.DataFrame,
    second_name: str,
    second_df: pd.DataFrame,
) -> None:

    first_df = first_df.copy()
    second_df = second_df.copy()

    first_df["normalized_statement"] = (
        first_df["statement"]
        .fillna("")
        .map(normalize_statement)
    )

    second_df["normalized_statement"] = (
        second_df["statement"]
        .fillna("")
        .map(normalize_statement)
    )

    overlap = set(
        first_df["normalized_statement"]
    ) & set(
        second_df["normalized_statement"]
    )

    print()
    print("=" * 70)
    print(f"🔎 {first_name.upper()} ↔ {second_name.upper()}")
    print("=" * 70)

    print()
    print(f"Exact normalized overlaps: {len(overlap)}")

    if not overlap:
        print("✅ No overlap.")
        return

    for index, statement in enumerate(
        sorted(overlap),
        start=1,
    ):

        first_matches = first_df[
            first_df["normalized_statement"] == statement
        ]

        second_matches = second_df[
            second_df["normalized_statement"] == statement
        ]

        print()
        print(f"--- Overlap #{index} ---")
        print()

        print("Statement:")
        print(f"  {statement}")

        print()
        print(f"{first_name} records:")

        for _, row in first_matches.iterrows():
            print(
                f"  ID: {row['id']} | "
                f"Label: {row['label']} | "
                f"Speaker: {row['speaker']}"
            )

        print()
        print(f"{second_name} records:")

        for _, row in second_matches.iterrows():
            print(
                f"  ID: {row['id']} | "
                f"Label: {row['label']} | "
                f"Speaker: {row['speaker']}"
            )


def main() -> None:

    print("=" * 70)
    print("🧿 VeriLens — LIAR2 Leakage Investigation")
    print("=" * 70)

    train = load_split("train")
    validation = load_split("validation")
    test = load_split("test")

    find_overlap(
        "train",
        train,
        "validation",
        validation,
    )

    find_overlap(
        "train",
        train,
        "test",
        test,
    )

    find_overlap(
        "validation",
        validation,
        "test",
        test,
    )

    print()
    print("=" * 70)
    print("✅ LEAKAGE INVESTIGATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()