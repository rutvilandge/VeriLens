from pathlib import Path
from collections import Counter

from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_ROOT = Path("ml/datasets/vision/cifake")
RAW_DIR = DATASET_ROOT / "raw"

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ============================================================
# HELPERS
# ============================================================

def find_images(directory: Path):
    """Return all supported image files recursively."""

    return [
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def inspect_images(images):
    """Inspect image dimensions, modes and formats."""

    width_counter = Counter()
    height_counter = Counter()
    mode_counter = Counter()
    format_counter = Counter()

    corrupted = []
    valid = []

    for index, image_path in enumerate(images, start=1):

        try:
            with Image.open(image_path) as image:

                image.verify()

            with Image.open(image_path) as image:

                width, height = image.size

                width_counter[width] += 1
                height_counter[height] += 1
                mode_counter[image.mode] += 1
                format_counter[image.format] += 1

            valid.append(image_path)

        except Exception as error:

            corrupted.append(
                {
                    "path": str(image_path),
                    "error": str(error),
                }
            )

        if index % 5000 == 0:

            print(
                f"Inspected {index:,} / "
                f"{len(images):,} images..."
            )

    return {
        "valid": valid,
        "corrupted": corrupted,
        "widths": width_counter,
        "heights": height_counter,
        "modes": mode_counter,
        "formats": format_counter,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("VeriLens — CIFAKE Dataset Inspection")
    print("=" * 70)

    print()
    print(f"Dataset directory: {RAW_DIR}")

    if not RAW_DIR.exists():

        raise FileNotFoundError(
            f"Dataset directory does not exist: {RAW_DIR}"
        )

    images = find_images(RAW_DIR)

    print()
    print(
        f"Images discovered: {len(images):,}"
    )

    if not images:

        print()
        print(
            "No images found."
        )

        print(
            "Place the CIFAKE dataset inside:"
        )

        print(
            f"  {RAW_DIR}"
        )

        return

    # --------------------------------------------------------
    # Detect likely class structure
    # --------------------------------------------------------

    class_counter = Counter()

    for image_path in images:

        relative_parts = image_path.relative_to(
            RAW_DIR
        ).parts

        if len(relative_parts) >= 2:

            class_name = relative_parts[0]

            class_counter[class_name] += 1

    print()
    print("=" * 70)
    print("CLASS DISTRIBUTION")
    print("=" * 70)

    if class_counter:

        for class_name, count in sorted(
            class_counter.items()
        ):

            print(
                f"{class_name:<25} {count:>8,}"
            )

    else:

        print(
            "No class folders detected."
        )

    # --------------------------------------------------------
    # Image inspection
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("IMAGE INSPECTION")
    print("=" * 70)

    results = inspect_images(images)

    valid_images = results["valid"]
    corrupted_images = results["corrupted"]

    print()
    print(
        f"Valid images:     {len(valid_images):,}"
    )

    print(
        f"Corrupted images: {len(corrupted_images):,}"
    )

    # --------------------------------------------------------
    # Dimensions
    # --------------------------------------------------------

    print()
    print("Image widths:")

    for width, count in results["widths"].most_common(10):

        print(
            f"  {width}px: {count:,}"
        )

    print()
    print("Image heights:")

    for height, count in results["heights"].most_common(10):

        print(
            f"  {height}px: {count:,}"
        )

    # --------------------------------------------------------
    # Modes
    # --------------------------------------------------------

    print()
    print("Color modes:")

    for mode, count in results["modes"].most_common():

        print(
            f"  {mode}: {count:,}"
        )

    # --------------------------------------------------------
    # Formats
    # --------------------------------------------------------

    print()
    print("Image formats:")

    for image_format, count in results["formats"].most_common():

        print(
            f"  {image_format}: {count:,}"
        )

    # --------------------------------------------------------
    # Corruption report
    # --------------------------------------------------------

    if corrupted_images:

        print()
        print("=" * 70)
        print("CORRUPTED IMAGE EXAMPLES")
        print("=" * 70)

        for item in corrupted_images[:10]:

            print()
            print(
                f"File: {item['path']}"
            )

            print(
                f"Error: {item['error']}"
            )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("DATASET INSPECTION COMPLETE")
    print("=" * 70)

    print()
    print(
        "Next step: create reproducible train/"
        "validation/test splits."
    )


if __name__ == "__main__":

    main()