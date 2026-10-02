from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent / "fakeddit"

RAW_DIR = ROOT / "raw" / "multimodal_only_samples"
OUTPUT_DIR = ROOT / "processed" / "cpu_subset"

SEED = 42

SPLITS = {
    "train": {
        "file": RAW_DIR / "multimodal_train.tsv",
        "samples_per_class": 5000,
    },
    "validation": {
        "file": RAW_DIR / "multimodal_validate.tsv",
        "samples_per_class": 1000,
    },
    "test": {
        "file": RAW_DIR / "multimodal_test_public.tsv",
        "samples_per_class": 1000,
    },
}


def create_subset(name: str, config: dict) -> None:
    print("\n" + "=" * 80)
    print(f"CREATING {name.upper()} SUBSET")
    print("=" * 80)

    df = pd.read_csv(config["file"], sep="\t")

    print(f"Original rows: {len(df):,}")

    # Keep only samples with both text and image URL.
    df["clean_title"] = df["clean_title"].fillna("").astype(str).str.strip()
    df["image_url"] = df["image_url"].fillna("").astype(str).str.strip()

    df = df[
        (df["clean_title"] != "")
        & (df["image_url"] != "")
        & df["2_way_label"].notna()
    ].copy()

    print(f"Rows with text + image URL: {len(df):,}")

    # Make sure labels are integers.
    df["2_way_label"] = df["2_way_label"].astype(int)

    selected_parts = []

    for label in [0, 1]:
        class_df = df[df["2_way_label"] == label]

        requested = config["samples_per_class"]

        if len(class_df) < requested:
            raise ValueError(
                f"Not enough samples for label {label}: "
                f"requested {requested}, available {len(class_df)}"
            )

        selected = class_df.sample(
            n=requested,
            random_state=SEED,
        )

        selected_parts.append(selected)

        print(
            f"Label {label}: selected {len(selected):,} "
            f"of {len(class_df):,}"
        )

    subset = pd.concat(selected_parts, ignore_index=True)

    # Shuffle the final subset.
    subset = subset.sample(
        frac=1.0,
        random_state=SEED,
    ).reset_index(drop=True)

    # Keep the columns required for the multimodal experiment,
    # plus useful metadata for analysis.
    columns = [
        "id",
        "clean_title",
        "title",
        "image_url",
        "domain",
        "subreddit",
        "created_utc",
        "2_way_label",
        "3_way_label",
        "6_way_label",
    ]

    subset = subset[[c for c in columns if c in subset.columns]]

    output_path = OUTPUT_DIR / f"{name}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subset.to_csv(output_path, index=False)

    print(f"\nSaved: {output_path}")
    print(f"Final rows: {len(subset):,}")

    print("\nLabel distribution:")
    print(
        subset["2_way_label"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nMissing image URLs:")
    print(subset["image_url"].isna().sum())

    print("\nMissing text:")
    print(
        subset["clean_title"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )


def main() -> None:
    print("=" * 80)
    print("FAKEDDIT MULTIMODAL CPU SUBSET")
    print("=" * 80)

    print(f"\nRandom seed: {SEED}")
    print(f"Output directory: {OUTPUT_DIR}")

    for name, config in SPLITS.items():
        create_subset(name, config)

    print("\n" + "=" * 80)
    print("CPU SUBSET CREATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()