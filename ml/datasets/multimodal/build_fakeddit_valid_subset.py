from pathlib import Path
import time

import pandas as pd
import requests
from PIL import Image
from io import BytesIO


ROOT = Path(__file__).resolve().parent / "fakeddit"

RAW_DIR = ROOT / "raw" / "multimodal_only_samples"
OUTPUT_DIR = ROOT / "processed" / "valid_subset"
IMAGE_DIR = OUTPUT_DIR / "images"

SEED = 42

TARGETS = {
    "train": 2000,
    "validation": 500,
    "test": 500,
}

FILES = {
    "train": RAW_DIR / "multimodal_train.tsv",
    "validation": RAW_DIR / "multimodal_validate.tsv",
    "test": RAW_DIR / "multimodal_test_public.tsv",
}

IMAGE_SIZE = (128, 128)
JPEG_QUALITY = 85

CONNECT_TIMEOUT = 5
READ_TIMEOUT = 8

MAX_RETRIES = 2

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/142.0 Safari/537.36"
)


def existing_ids(split: str) -> set[str]:
    """
    Find already downloaded images for this split.
    """

    directory = IMAGE_DIR / split

    if not directory.exists():
        return set()

    return {
        path.stem
        for path in directory.glob("*.jpg")
    }


def download_image(
    session: requests.Session,
    url: str,
    output_path: Path,
) -> tuple[bool, str]:

    if output_path.exists() and output_path.stat().st_size > 0:
        try:
            with Image.open(output_path) as image:
                image.verify()

            return True, "existing"

        except Exception:
            output_path.unlink(missing_ok=True)

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            response = session.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                stream=True,
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type",
                "",
            ).lower()

            if content_type and not content_type.startswith("image/"):
                return False, f"not_image:{content_type}"

            # Read only the response body after the server has responded.
            data = response.content

            if not data:
                return False, "empty_response"

            with Image.open(BytesIO(data)) as image:

                image.load()

                image = image.convert("RGB")

                image.thumbnail(
                    IMAGE_SIZE,
                    Image.Resampling.LANCZOS,
                )

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
                    "JPEG",
                    quality=JPEG_QUALITY,
                    optimize=True,
                )

            with Image.open(output_path) as check:
                check.verify()

            return True, "downloaded"

        except requests.exceptions.HTTPError as exc:

            status = getattr(
                exc.response,
                "status_code",
                None,
            )

            if status == 404:
                return False, "404"

            return False, f"http_{status}"

        except requests.exceptions.Timeout:

            if attempt == MAX_RETRIES:
                return False, "timeout"

        except requests.exceptions.RequestException as exc:

            if attempt == MAX_RETRIES:
                return False, f"request_error:{type(exc).__name__}"

        except Exception as exc:

            return False, f"image_error:{type(exc).__name__}"

        time.sleep(0.5)

    return False, "failed"


def load_candidates(split: str) -> pd.DataFrame:

    path = FILES[split]

    df = pd.read_csv(path, sep="\t")

    df["clean_title"] = (
        df["clean_title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["image_url"] = (
        df["image_url"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["2_way_label"] = df["2_way_label"].astype(int)

    # Only genuine text + image samples.
    df = df[
        (df["clean_title"] != "")
        & (df["image_url"] != "")
    ].copy()

    # Deterministic shuffle.
    df = df.sample(
        frac=1,
        random_state=SEED,
    ).reset_index(drop=True)

    return df


def build_split(
    session: requests.Session,
    split: str,
    target_total: int,
) -> pd.DataFrame:

    print("\n" + "=" * 80)
    print(f"BUILDING VALID {split.upper()} SET")
    print("=" * 80)

    df = load_candidates(split)

    print(
        f"Available candidates: {len(df):,}"
    )

    split_dir = IMAGE_DIR / split
    split_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing = existing_ids(split)

    if existing:
        print(
            f"Existing valid images: {len(existing):,}"
        )

    selected = []
    selected_ids = set(existing)

    # Reuse existing images by matching them to metadata.
    if existing:
        existing_rows = df[
            df["id"].astype(str).isin(existing)
        ].copy()

        selected.extend(
            existing_rows.to_dict("records")
        )

    current_counts = {
        0: sum(
            int(row["2_way_label"]) == 0
            for row in selected
        ),
        1: sum(
            int(row["2_way_label"]) == 1
            for row in selected
        ),
    }

    target_per_class = target_total // 2

    print(
        f"Existing class counts: "
        f"label0={current_counts[0]}, "
        f"label1={current_counts[1]}"
    )

    failures = {
        "404": 0,
        "timeout": 0,
        "other": 0,
    }

    attempts = 0

    for _, row in df.iterrows():

        if (
            current_counts[0] >= target_per_class
            and current_counts[1] >= target_per_class
        ):
            break

        sample_id = str(row["id"])
        label = int(row["2_way_label"])

        if sample_id in selected_ids:
            continue

        if current_counts[label] >= target_per_class:
            continue

        attempts += 1

        output_path = (
            split_dir / f"{sample_id}.jpg"
        )

        success, status = download_image(
            session,
            row["image_url"],
            output_path,
        )

        if success:

            selected.append(
                row.to_dict()
            )

            selected_ids.add(sample_id)
            current_counts[label] += 1

            if (
                current_counts[label] % 100 == 0
                or len(selected) == target_total
            ):
                print(
                    f"Progress: "
                    f"{len(selected):,}/{target_total:,} "
                    f"| label0={current_counts[0]} "
                    f"| label1={current_counts[1]}"
                )

        else:

            if status == "404":
                failures["404"] += 1

            elif status == "timeout":
                failures["timeout"] += 1

            else:
                failures["other"] += 1

            if attempts % 100 == 0:
                print(
                    f"Checked {attempts:,} candidates | "
                    f"valid={len(selected):,} | "
                    f"404={failures['404']:,} | "
                    f"timeout={failures['timeout']:,}"
                )

    if len(selected) < target_total:

        raise RuntimeError(
            f"\nCould not build {split} set.\n"
            f"Required: {target_total}\n"
            f"Obtained: {len(selected)}\n"
            f"Try increasing the candidate pool."
        )

    result = pd.DataFrame(selected)

    # Final deterministic shuffle.
    result = result.sample(
        frac=1,
        random_state=SEED,
    ).reset_index(drop=True)

    output_columns = [
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

    result = result[
        [
            column
            for column in output_columns
            if column in result.columns
        ]
    ]

    csv_path = (
        OUTPUT_DIR / f"{split}.csv"
    )

    csv_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        csv_path,
        index=False,
    )

    print("\nFinal split:")
    print(f"Rows: {len(result):,}")

    print("\nLabels:")
    print(
        result["2_way_label"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print(
        f"\nSaved metadata:\n{csv_path}"
    )

    print(
        f"\nImage directory:\n{split_dir}"
    )

    return result


def main() -> None:

    print("=" * 80)
    print("FAKEDDIT VALID MULTIMODAL CPU DATASET")
    print("=" * 80)

    print("\nTargets:")

    for split, target in TARGETS.items():
        print(
            f"  {split:12s}: {target:,}"
        )

    print(
        f"\nImage size: "
        f"{IMAGE_SIZE[0]}x{IMAGE_SIZE[1]}"
    )

    print(
        f"Output:\n{OUTPUT_DIR}"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    session = requests.Session()

    results = {}

    for split, target in TARGETS.items():

        results[split] = build_split(
            session,
            split,
            target,
        )

    print("\n" + "=" * 80)
    print("FAKEDDIT VALID SUBSET COMPLETE")
    print("=" * 80)

    for split, df in results.items():

        image_count = len(
            list(
                (
                    IMAGE_DIR / split
                ).glob("*.jpg")
            )
        )

        print(
            f"{split:12s}: "
            f"{len(df):,} metadata rows | "
            f"{image_count:,} images"
        )


if __name__ == "__main__":
    main()