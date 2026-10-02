from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent / "fakeddit" / "raw" / "multimodal_only_samples"

FILES = {
    "train": ROOT / "multimodal_train.tsv",
    "validation": ROOT / "multimodal_validate.tsv",
    "test": ROOT / "multimodal_test_public.tsv",
}


def inspect_split(name: str, path: Path) -> pd.DataFrame:
    print("\n" + "=" * 80)
    print(f"{name.upper()} SPLIT")
    print("=" * 80)

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path, sep="\t")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nFirst 3 rows:")
    print(df.head(3).to_string())

    print("\nMissing values:")
    missing = df.isna().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("  None")
    else:
        print(missing.to_string())

    print("\nDuplicate IDs:")

    if "id" in df.columns:
        duplicate_ids = df["id"].duplicated().sum()
        print(f"  {duplicate_ids:,}")

    print("\nPotential label columns:")

    for column in ["2_way_label", "3_way_label", "6_way_label", "label"]:
        if column in df.columns:
            print(f"\n{column}:")
            print(df[column].value_counts(dropna=False).sort_index().to_string())

    print("\nPotential text columns:")

    for column in ["clean_title", "title", "post_text", "body", "text"]:
        if column in df.columns:
            non_empty = df[column].fillna("").astype(str).str.strip().ne("").sum()
            print(f"  {column}: {non_empty:,} non-empty")

    print("\nPotential image columns:")

    for column in ["image_url", "image_url_clean", "image"]:
        if column in df.columns:
            non_empty = df[column].fillna("").astype(str).str.strip().ne("").sum()
            print(f"  {column}: {non_empty:,} non-empty")

    return df


def main() -> None:
    print("=" * 80)
    print("FAKEDDIT MULTIMODAL DATASET INSPECTION")
    print("=" * 80)

    print(f"\nDataset directory:\n{ROOT}")

    datasets = {}

    for name, path in FILES.items():
        datasets[name] = inspect_split(name, path)

    print("\n" + "=" * 80)
    print("SPLIT SUMMARY")
    print("=" * 80)

    for name, df in datasets.items():
        print(f"{name:12s}: {len(df):,} rows")

    print("\nInspection complete.")


if __name__ == "__main__":
    main()