from pathlib import Path
import random
import shutil

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_DIR = PROJECT_ROOT / "ml" / "datasets" / "vision" / "cifake"
SPLITS_DIR = DATASET_DIR / "splits"
CPU_DIR = DATASET_DIR / "cpu_subset"

SEED = 42

COUNTS = {
    "train": 5000,
    "validation": 1000,
    "test": 1000,
}

CLASSES = ["real", "fake"]

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def collect_images(directory):
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def main():

    print("=" * 70)
    print("VeriLens — CIFAKE CPU Experiment Subset")
    print("=" * 70)

    random.seed(SEED)

    if CPU_DIR.exists():
        print()
        print(f"Removing existing subset: {CPU_DIR}")
        shutil.rmtree(CPU_DIR)

    total_created = 0

    for split_name, count_per_class in COUNTS.items():

        print()
        print("-" * 70)
        print(f"Creating split: {split_name}")

        for class_name in CLASSES:

            source_dir = SPLITS_DIR / split_name / class_name
            destination_dir = CPU_DIR / split_name / class_name

            destination_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            images = collect_images(source_dir)

            if len(images) < count_per_class:
                raise ValueError(
                    f"Not enough {class_name} images in {split_name}. "
                    f"Found {len(images)}, need {count_per_class}."
                )

            selected = random.sample(
                images,
                count_per_class,
            )

            for image_path in selected:

                shutil.copy2(
                    image_path,
                    destination_dir / image_path.name,
                )

            print(
                f"{class_name:<6} "
                f"{len(selected):,} images"
            )

            total_created += len(selected)

    print()
    print("=" * 70)
    print("CPU SUBSET COMPLETE")
    print("=" * 70)

    print()
    print(f"Total images created: {total_created:,}")

    print()
    print("Structure:")

    for split_name, count_per_class in COUNTS.items():

        total = count_per_class * len(CLASSES)

        print(
            f"  {split_name:<12} "
            f"{total:,} "
            f"({count_per_class:,} real + "
            f"{count_per_class:,} fake)"
        )

    print()
    print(f"Output:")
    print(CPU_DIR)

    print()
    print(f"Random seed: {SEED}")


if __name__ == "__main__":
    main()