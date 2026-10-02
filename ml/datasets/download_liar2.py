from pathlib import Path
import json

from datasets import load_dataset


# ---------------------------------------------------------
# VeriLens — LIAR2 Dataset Downloader
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "liar2"

DATASET_NAME = "chengxuphd/liar2"


def main() -> None:
    print("=" * 70)
    print("🧿 VeriLens — LIAR2 Dataset Setup")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print(f"📦 Dataset: {DATASET_NAME}")
    print(f"📁 Output:  {OUTPUT_DIR}")
    print()

    print("⬇️ Downloading dataset from Hugging Face...")
    print()

    dataset = load_dataset(DATASET_NAME)

    print("✅ Dataset downloaded successfully.")
    print()

    metadata = {
        "dataset_name": DATASET_NAME,
        "purpose": "Text credibility and misinformation classification benchmark",
        "source": "Hugging Face",
        "license": "Apache-2.0",
        "splits": {},
        "columns": {},
    }

    for split_name, split_dataset in dataset.items():
        print(f"🔎 Processing split: {split_name}")

        dataframe = split_dataset.to_pandas()

        output_file = OUTPUT_DIR / f"{split_name}.csv"

        dataframe.to_csv(
            output_file,
            index=False,
            encoding="utf-8",
        )

        metadata["splits"][split_name] = {
            "rows": len(dataframe),
            "columns": list(dataframe.columns),
            "file": str(output_file.relative_to(PROJECT_ROOT)),
        }

        metadata["columns"][split_name] = {
            column: str(dataframe[column].dtype)
            for column in dataframe.columns
        }

        print(f"   Rows:    {len(dataframe):,}")
        print(f"   Columns: {len(dataframe.columns)}")
        print(f"   Saved:   {output_file}")
        print()

    metadata_file = OUTPUT_DIR / "metadata.json"

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

    print("=" * 70)
    print("✅ LIAR2 DATASET READY")
    print("=" * 70)
    print()
    print(f"📁 Location: {OUTPUT_DIR}")
    print()
    print("Files created:")

    for file in sorted(OUTPUT_DIR.iterdir()):
        print(f"   • {file.name}")

    print()
    print("Next step: inspect the dataset before preprocessing.")
    print("=" * 70)


if __name__ == "__main__":
    main()