from pathlib import Path
import csv
import random
import shutil

DATASET_ROOT = Path("ml/datasets/vision/cifake")
RAW_DIR = DATASET_ROOT / "raw"
SPLITS_DIR = DATASET_ROOT / "splits"

SEED = 42
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

CLASSES = {
    "real": 0,
    "fake": 1,
}


def collect_images(class_name: str):
    class_dir = RAW_DIR / class_name

    if not class_dir.exists():
        raise FileNotFoundError(
            f"Expected class directory does not exist: {class_dir}"
        )

    images = sorted(
        path
        for path in class_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".webp",
        }
    )

    return images


def split_images(images):
    shuffled = images.copy()
    random.shuffle(shuffled)

    total = len(shuffled)
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_images = shuffled[:train_end]
    val_images = shuffled[train_end:val_end]
    test_images = shuffled[val_end:]

    return train_images, val_images, test_images


def write_manifest(rows, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "path",
                "filename",
                "label_name",
                "label",
                "split",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)


def copy_split(images, class_name, split_name):
    destination = SPLITS_DIR / split_name / class_name
    destination.mkdir(parents=True, exist_ok=True)

    rows = []

    for image_path in images:
        destination_path = destination / image_path.name

        shutil.copy2(image_path, destination_path)

        rows.append(
            {
                "path": str(destination_path).replace("\\", "/"),
                "filename": image_path.name,
                "label_name": class_name,
                "label": CLASSES[class_name],
                "split": split_name,
            }
        )

    return rows


def main():
    print("=" * 70)
    print("VeriLens — CIFAKE Reproducible Dataset Split")
    print("=" * 70)

    print()
    print(f"Dataset: {RAW_DIR}")
    print(f"Random seed: {SEED}")
    print(f"Train ratio: {TRAIN_RATIO:.0%}")
    print(f"Validation ratio: {VAL_RATIO:.0%}")
    print(f"Test ratio: {TEST_RATIO:.0%}")

    if abs(TRAIN_RATIO + VAL_RATIO + TEST_RATIO - 1.0) > 1e-9:
        raise ValueError("Split ratios must sum to 1.0.")

    random.seed(SEED)

    all_rows = []

    for class_name in CLASSES:
        print()
        print("-" * 70)
        print(f"Processing class: {class_name}")

        images = collect_images(class_name)

        print(f"Images found: {len(images):,}")

        train_images, val_images, test_images = split_images(images)

        print(f"Train:      {len(train_images):,}")
        print(f"Validation: {len(val_images):,}")
        print(f"Test:       {len(test_images):,}")

        train_rows = copy_split(
            train_images,
            class_name,
            "train",
        )

        val_rows = copy_split(
            val_images,
            class_name,
            "validation",
        )

        test_rows = copy_split(
            test_images,
            class_name,
            "test",
        )

        all_rows.extend(train_rows)
        all_rows.extend(val_rows)
        all_rows.extend(test_rows)

    train_rows = [row for row in all_rows if row["split"] == "train"]
    val_rows = [row for row in all_rows if row["split"] == "validation"]
    test_rows = [row for row in all_rows if row["split"] == "test"]

    write_manifest(
        train_rows,
        SPLITS_DIR / "train.csv",
    )

    write_manifest(
        val_rows,
        SPLITS_DIR / "validation.csv",
    )

    write_manifest(
        test_rows,
        SPLITS_DIR / "test.csv",
    )

    print()
    print("=" * 70)
    print("FINAL SPLIT SUMMARY")
    print("=" * 70)

    print(f"Total:      {len(all_rows):,}")
    print(f"Train:      {len(train_rows):,}")
    print(f"Validation: {len(val_rows):,}")
    print(f"Test:       {len(test_rows):,}")

    print()
    print("Class distribution:")

    for split_name, rows in [
        ("train", train_rows),
        ("validation", val_rows),
        ("test", test_rows),
    ]:
        real_count = sum(
            row["label_name"] == "real"
            for row in rows
        )

        fake_count = sum(
            row["label_name"] == "fake"
            for row in rows
        )

        print(
            f"{split_name:<12} "
            f"real={real_count:,} "
            f"fake={fake_count:,}"
        )

    print()
    print("Output directory:")
    print(SPLITS_DIR)

    print()
    print("Generated manifests:")
    print(f"  {SPLITS_DIR / 'train.csv'}")
    print(f"  {SPLITS_DIR / 'validation.csv'}")
    print(f"  {SPLITS_DIR / 'test.csv'}")

    print()
    print("=" * 70)
    print("CIFAKE SPLITTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()