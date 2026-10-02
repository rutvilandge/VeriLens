from pathlib import Path
import time

import pandas as pd
import requests
from PIL import Image
from io import BytesIO


ROOT = Path(__file__).resolve().parent / "fakeddit"

SUBSET_DIR = ROOT / "processed" / "cpu_subset"
IMAGE_DIR = ROOT / "processed" / "images"

SPLITS = {
    "train": SUBSET_DIR / "train.csv",
    "validation": SUBSET_DIR / "validation.csv",
    "test": SUBSET_DIR / "test.csv",
}

IMAGE_SIZE = (128, 128)
JPEG_QUALITY = 85

TIMEOUT = 15
MAX_RETRIES = 3

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/142.0 Safari/537.36"
)


def download_image(
    session: requests.Session,
    url: str,
    output_path: Path,
) -> tuple[bool, str]:
    """
    Download, validate, resize, and save one image.

    Returns:
        (success, status)
    """

    if output_path.exists() and output_path.stat().st_size > 0:
        try:
            with Image.open(output_path) as image:
                image.verify()

            return True, "already_exists"

        except Exception:
            output_path.unlink(missing_ok=True)

    last_error = "unknown_error"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(
                url,
                timeout=TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type",
                "",
            ).lower()

            # Some Reddit image endpoints may not provide a perfect
            # content type, so PIL remains the final authority.
            if content_type and not content_type.startswith("image/"):
                last_error = f"not_image_content_type:{content_type}"
                continue

            with Image.open(BytesIO(response.content)) as image:
                image.load()

                image = image.convert("RGB")

                image.thumbnail(IMAGE_SIZE, Image.Resampling.LANCZOS)

                canvas = Image.new(
                    "RGB",
                    IMAGE_SIZE,
                    (255, 255, 255),
                )

                x = (IMAGE_SIZE[0] - image.width) // 2
                y = (IMAGE_SIZE[1] - image.height) // 2

                canvas.paste(image, (x, y))

                output_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                canvas.save(
                    output_path,
                    format="JPEG",
                    quality=JPEG_QUALITY,
                    optimize=True,
                )

            # Final validation.
            with Image.open(output_path) as check:
                check.verify()

            return True, "downloaded"

        except requests.RequestException as exc:
            last_error = f"request_error:{exc}"

        except Exception as exc:
            last_error = f"image_error:{exc}"

        if attempt < MAX_RETRIES:
            time.sleep(1.5 * attempt)

    return False, last_error


def process_split(
    session: requests.Session,
    split_name: str,
    csv_path: Path,
) -> list[dict]:
    print("\n" + "=" * 80)
    print(f"DOWNLOADING {split_name.upper()} IMAGES")
    print("=" * 80)

    df = pd.read_csv(csv_path)

    split_dir = IMAGE_DIR / split_name
    split_dir.mkdir(parents=True, exist_ok=True)

    failures = []

    total = len(df)

    for index, row in df.iterrows():
        sample_id = str(row["id"])
        url = str(row["image_url"]).strip()

        output_path = split_dir / f"{sample_id}.jpg"

        success, status = download_image(
            session,
            url,
            output_path,
        )

        current = index + 1

        if not success:
            failures.append(
                {
                    "id": sample_id,
                    "image_url": url,
                    "error": status,
                }
            )

            print(
                f"[{current:,}/{total:,}] "
                f"FAILED {sample_id} → {status}"
            )

        elif status == "already_exists":
            if current % 250 == 0 or current == total:
                print(
                    f"[{current:,}/{total:,}] "
                    f"already processed"
                )

        else:
            if current % 100 == 0 or current == total:
                print(
                    f"[{current:,}/{total:,}] "
                    f"downloaded"
                )

    failure_path = (
        SUBSET_DIR / f"{split_name}_download_failures.csv"
    )

    if failures:
        pd.DataFrame(failures).to_csv(
            failure_path,
            index=False,
        )

        print(
            f"\nFailed downloads: {len(failures):,}"
        )

        print(
            f"Failure log: {failure_path}"
        )

    else:
        # Remove stale failure log from an earlier run.
        failure_path.unlink(missing_ok=True)

        print("\nNo download failures.")

    successful = total - len(failures)

    print(
        f"Successful images: "
        f"{successful:,}/{total:,}"
    )

    return failures


def main() -> None:
    print("=" * 80)
    print("FAKEDDIT MULTIMODAL IMAGE DOWNLOADER")
    print("=" * 80)

    print(f"\nImage size: {IMAGE_SIZE[0]}x{IMAGE_SIZE[1]}")
    print(f"JPEG quality: {JPEG_QUALITY}")
    print(f"Output directory: {IMAGE_DIR}")

    IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    session = requests.Session()

    all_failures = []

    for split_name, csv_path in SPLITS.items():
        failures = process_split(
            session,
            split_name,
            csv_path,
        )

        all_failures.extend(
            [
                {
                    "split": split_name,
                    **failure,
                }
                for failure in failures
            ]
        )

    print("\n" + "=" * 80)
    print("IMAGE DOWNLOAD COMPLETE")
    print("=" * 80)

    total_requested = sum(
        len(pd.read_csv(path))
        for path in SPLITS.values()
    )

    print(f"\nTotal requested: {total_requested:,}")
    print(f"Total failures: {len(all_failures):,}")
    print(
        f"Total successful: "
        f"{total_requested - len(all_failures):,}"
    )

    if all_failures:
        combined_failure_path = (
            SUBSET_DIR / "all_download_failures.csv"
        )

        pd.DataFrame(all_failures).to_csv(
            combined_failure_path,
            index=False,
        )

        print(
            f"\nCombined failure log:"
            f"\n{combined_failure_path}"
        )


if __name__ == "__main__":
    main()