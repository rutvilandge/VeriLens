from pathlib import Path
import json
import re


# ============================================================
# VERILENS
# PHASE 7.1 — CLAIM EXTRACTION & NORMALIZATION
# ============================================================

OUTPUT_DIR = Path(
    "ml/evidence/artifacts"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "claim_extraction_examples.json"
)


# ============================================================
# REGEX PATTERNS
# ============================================================

TEMPORAL_PATTERN = re.compile(
    r"\b("
    r"19\d{2}|20\d{2}|"
    r"January|February|March|April|May|June|"
    r"July|August|September|October|November|December"
    r")\b",
    re.IGNORECASE,
)

NUMERIC_PATTERN = re.compile(
    r"""
    (
        \b\d+(?:\.\d+)?\s*%
        |
        \$\s*\d+(?:\.\d+)?
        |
        \b\d+(?:\.\d+)?\s*
        (?:million|billion|trillion|thousand)
        |
        \b\d+(?:\.\d+)?\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

COMPARATIVE_PATTERN = re.compile(
    r"\b("
    r"more|less|higher|lower|greater|smaller|"
    r"increased|decreased|rose|fell|dropped|"
    r"grew|declined|doubled|halved|"
    r"remained|"
    r")\b",
    re.IGNORECASE,
)

CAUSAL_PATTERN = re.compile(
    r"\b("
    r"because|therefore|caused|led to|resulted in|"
    r"due to|as a result"
    r")\b",
    re.IGNORECASE,
)


# ============================================================
# SENTENCE SPLITTING
# ============================================================

def split_sentences(text):
    """
    Split input text into individual sentences.
    """

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# CLAIM TYPE CLASSIFICATION
# ============================================================

def classify_claim_type(sentence):
    """
    Assign a structural claim category.

    Priority:
        numeric
        causal
        comparative
        temporal
        general
    """

    if NUMERIC_PATTERN.search(sentence):
        return "numeric"

    if CAUSAL_PATTERN.search(sentence):
        return "causal"

    if COMPARATIVE_PATTERN.search(sentence):
        return "comparative"

    if TEMPORAL_PATTERN.search(sentence):
        return "temporal"

    return "general"


# ============================================================
# TIME REFERENCE EXTRACTION
# ============================================================

def extract_time_references(sentence):
    """
    Extract years and month names.
    """

    matches = TEMPORAL_PATTERN.findall(
        sentence
    )

    return list(
        dict.fromkeys(
            match.lower()
            for match in matches
        )
    )


# ============================================================
# NUMERIC REFERENCE EXTRACTION
# ============================================================

def extract_numeric_references(sentence):
    """
    Extract percentages, currency values,
    quantities and standalone numbers.
    """

    matches = NUMERIC_PATTERN.findall(
        sentence
    )

    cleaned = []

    for match in matches:

        value = re.sub(
            r"\s+",
            " ",
            match.strip(),
        )

        cleaned.append(value)

    return cleaned


# ============================================================
# SIMPLE ENTITY EXTRACTION
# ============================================================

def extract_entities(sentence):
    """
    Lightweight entity extraction based on
    capitalized words.

    This is intentionally deterministic.
    A stronger NER model can be introduced later.
    """

    candidates = re.findall(
        r"\b[A-Z][a-zA-Z]{2,}"
        r"(?:\s+[A-Z][a-zA-Z]{2,})*\b",
        sentence,
    )

    stopwords = {
        "The",
        "This",
        "That",
        "These",
        "Those",
        "According",
        "However",
        "Meanwhile",
        "After",
        "Before",
        "While",
        "Because",
    }

    entities = [
        candidate
        for candidate in candidates
        if candidate not in stopwords
    ]

    return list(
        dict.fromkeys(
            entities
        )
    )


# ============================================================
# CLAIM NORMALIZATION
# ============================================================

def normalize_claim(sentence):
    """
    Normalize whitespace and surrounding quotes
    while preserving the original wording.
    """

    normalized = re.sub(
        r"\s+",
        " ",
        sentence,
    ).strip()

    normalized = normalized.strip(
        "\"'"
    )

    return normalized


# ============================================================
# CLAIM EXTRACTION
# ============================================================

def extract_claims(text):
    """
    Convert input text into structured claims.
    """

    sentences = split_sentences(
        text
    )

    claims = []

    for index, sentence in enumerate(
        sentences,
        start=1,
    ):

        normalized = normalize_claim(
            sentence
        )

        # Ignore extremely short fragments.
        if len(normalized) < 10:
            continue

        claim = {
            "claim_id": (
                f"claim_{index:04d}"
            ),

            "claim_text": normalized,

            "claim_type": (
                classify_claim_type(
                    normalized
                )
            ),

            "entities": (
                extract_entities(
                    normalized
                )
            ),

            "time_references": (
                extract_time_references(
                    normalized
                )
            ),

            "numeric_references": (
                extract_numeric_references(
                    normalized
                )
            ),

            "status": "unverified",
        }

        claims.append(
            claim
        )

    return claims


# ============================================================
# DEMO INPUTS
# ============================================================

EXAMPLES = [
    (
        "The unemployment rate dropped to 3% in 2024, "
        "while inflation remained below 4%."
    ),

    (
        "Apple reported record revenue of $100 billion "
        "after demand increased significantly."
    ),

    (
        "The policy was introduced in 2020 because "
        "the government wanted to reduce emissions."
    ),

    (
        "The company opened a new manufacturing facility "
        "in Pune."
    ),
]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "VERILENS - PHASE 7.1"
    )
    print(
        "CLAIM EXTRACTION & NORMALIZATION"
    )
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_results = []

    for example_index, text in enumerate(
        EXAMPLES,
        start=1,
    ):

        print(
            f"\n{'-' * 70}"
        )

        print(
            f"EXAMPLE {example_index}"
        )

        print(
            f"{'-' * 70}"
        )

        print(
            f"Input:\n{text}"
        )

        claims = extract_claims(
            text
        )

        print(
            f"\nExtracted claims: "
            f"{len(claims)}"
        )

        for claim in claims:

            print(
                "\nClaim:"
            )

            print(
                f"  ID: "
                f"{claim['claim_id']}"
            )

            print(
                f"  Text: "
                f"{claim['claim_text']}"
            )

            print(
                f"  Type: "
                f"{claim['claim_type']}"
            )

            print(
                f"  Entities: "
                f"{claim['entities']}"
            )

            print(
                f"  Time: "
                f"{claim['time_references']}"
            )

            print(
                f"  Numeric: "
                f"{claim['numeric_references']}"
            )

            print(
                f"  Status: "
                f"{claim['status']}"
            )

        all_results.append(
            {
                "example_id": example_index,
                "input_text": text,
                "claims": claims,
            }
        )

    # ========================================================
    # SAVE ARTIFACT
    # ========================================================

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            all_results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    total_claims = sum(
        len(item["claims"])
        for item in all_results
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "CLAIM EXTRACTION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Examples processed: "
        f"{len(all_results)}"
    )

    print(
        f"Claims extracted: "
        f"{total_claims}"
    )

    print(
        f"Saved artifact:"
    )

    print(
        OUTPUT_PATH
    )

    print(
        "=" * 70
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()