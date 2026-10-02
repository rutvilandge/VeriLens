from pathlib import Path
import json
import re
from datetime import datetime, timezone

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# VERILENS
# PHASE 7.4 — SUPPORT / CONTRADICTION CLASSIFICATION
# ============================================================

OUTPUT_DIR = Path("ml/evidence/artifacts")

OUTPUT_PATH = (
    OUTPUT_DIR / "evidence_relation_examples.json"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for comparison.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = re.sub(
        r"[^\w\s%.-]",
        "",
        text,
    )

    return text.strip()


# ============================================================
# TOKEN EXTRACTION
# ============================================================

def extract_tokens(text):
    """
    Extract normalized tokens.
    """

    return set(
        normalize_text(text).split()
    )


# ============================================================
# NUMERIC EXTRACTION
# ============================================================

def extract_numeric_references(text):
    """
    Extract percentages, years, and numeric values.
    """

    normalized = normalize_text(text)

    patterns = [
        r"\b\d+(?:\.\d+)?%",
        r"\b(?:19|20)\d{2}\b",
        r"\b\d+(?:\.\d+)?\s*(?:million|billion|trillion|thousand)\b",
        r"\$\s*\d+(?:\.\d+)?",
        r"\b\d+(?:\.\d+)?\b",
    ]

    values = []

    for pattern in patterns:

        values.extend(
            re.findall(
                pattern,
                normalized,
            )
        )

    return set(values)


# ============================================================
# KEY PHRASE EXTRACTION
# ============================================================

def extract_key_phrases(text):
    """
    Extract important domain phrases.
    """

    normalized = normalize_text(text)

    phrase_patterns = [
        r"\bunemployment rate\b",
        r"\binflation rate\b",
        r"\bpopulation\b",
        r"\beconomic growth\b",
        r"\bgdp\b",
        r"\binterest rate\b",
        r"\bcrime rate\b",
        r"\bpoverty rate\b",
        r"\bapproval rating\b",
        r"\bdeath rate\b",
        r"\bemployment rate\b",
        r"\bhealthcare spending\b",
        r"\bgovernment spending\b",
        r"\bcarbon emissions\b",
        r"\bclimate change\b",
    ]

    phrases = set()

    for pattern in phrase_patterns:

        matches = re.findall(
            pattern,
            normalized,
        )

        phrases.update(matches)

    return phrases


# ============================================================
# NEGATION DETECTION
# ============================================================

def contains_negation(text):
    """
    Detect common negation words.
    """

    normalized = normalize_text(text)

    negation_words = {
        "not",
        "no",
        "never",
        "neither",
        "without",
        "didnt",
        "didnt",
        "doesnt",
        "dont",
        "isnt",
        "wasnt",
        "werent",
        "cannot",
        "couldnt",
        "wouldnt",
        "shouldnt",
        "unlikely",
    }

    tokens = set(
        normalized.split()
    )

    return bool(
        tokens & negation_words
    )


# ============================================================
# NUMERIC AGREEMENT
# ============================================================

def calculate_numeric_agreement(
    claim,
    evidence,
):
    """
    Compare numeric references between
    claim and evidence.
    """

    claim_numbers = (
        extract_numeric_references(
            claim
        )
    )

    evidence_numbers = (
        extract_numeric_references(
            evidence
        )
    )

    if not claim_numbers:
        return 0.5

    overlap = (
        claim_numbers
        & evidence_numbers
    )

    return round(
        len(overlap)
        / len(claim_numbers),
        4,
    )


# ============================================================
# PHRASE AGREEMENT
# ============================================================

def calculate_phrase_agreement(
    claim,
    evidence,
):
    """
    Compare important domain phrases.
    """

    claim_phrases = (
        extract_key_phrases(
            claim
        )
    )

    evidence_phrases = (
        extract_key_phrases(
            evidence
        )
    )

    if not claim_phrases:
        return 0.5

    overlap = (
        claim_phrases
        & evidence_phrases
    )

    return round(
        len(overlap)
        / len(claim_phrases),
        4,
    )


# ============================================================
# TOKEN OVERLAP
# ============================================================

def calculate_token_overlap(
    claim,
    evidence,
):
    """
    Calculate token-level overlap.
    """

    claim_tokens = extract_tokens(
        claim
    )

    evidence_tokens = extract_tokens(
        evidence
    )

    if not claim_tokens:
        return 0.0

    overlap = (
        claim_tokens
        & evidence_tokens
    )

    return round(
        len(overlap)
        / len(claim_tokens),
        4,
    )


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def calculate_semantic_similarity(
    claim,
    evidence,
):
    """
    Calculate TF-IDF cosine similarity
    between claim and evidence.
    """

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )

    matrix = vectorizer.fit_transform(
        [
            normalize_text(claim),
            normalize_text(evidence),
        ]
    )

    similarity = cosine_similarity(
        matrix[0],
        matrix[1],
    )[0][0]

    return round(
        float(similarity),
        4,
    )


# ============================================================
# CONTRADICTION INDICATORS
# ============================================================

def detect_contradiction_indicators(
    claim,
    evidence,
):
    """
    Detect simple contradiction patterns.

    This is intentionally conservative.
    It does NOT attempt full natural-language
    inference.
    """

    claim_normalized = normalize_text(
        claim
    )

    evidence_normalized = normalize_text(
        evidence
    )

    indicators = []

    # --------------------------------------------------------
    # Explicit contradiction phrases
    # --------------------------------------------------------

    contradiction_phrases = [
        "contrary to",
        "in contrast",
        "however",
        "but",
        "disagrees",
        "disputed",
        "incorrect",
        "false",
        "not true",
        "no evidence",
        "did not",
        "does not",
        "was not",
        "were not",
    ]

    for phrase in contradiction_phrases:

        if phrase in evidence_normalized:

            indicators.append(
                phrase
            )

    # --------------------------------------------------------
    # Negation mismatch
    # --------------------------------------------------------

    claim_negation = (
        contains_negation(
            claim_normalized
        )
    )

    evidence_negation = (
        contains_negation(
            evidence_normalized
        )
    )

    if (
        claim_negation
        != evidence_negation
    ):

        indicators.append(
            "negation_mismatch"
        )

    return indicators


# ============================================================
# NUMERIC CONTRADICTION
# ============================================================

def detect_numeric_contradiction(
    claim,
    evidence,
):
    """
    Detect whether numeric values relevant
    to the claim differ in the evidence.
    """

    claim_numbers = (
        extract_numeric_references(
            claim
        )
    )

    evidence_numbers = (
        extract_numeric_references(
            evidence
        )
    )

    if not claim_numbers:
        return False

    if not evidence_numbers:
        return False

    overlap = (
        claim_numbers
        & evidence_numbers
    )

    # If the evidence contains numbers but
    # none of the claim's important numbers,
    # mark this only as a possible mismatch.
    if not overlap:

        return True

    return False


# ============================================================
# RELATION CLASSIFICATION
# ============================================================

def classify_relation(
    claim,
    evidence,
):
    """
    Classify evidence as:

    - supports
    - contradicts
    - neutral

    This is a transparent Phase 7.4
    prototype rather than a full NLI model.
    """

    semantic_similarity = (
        calculate_semantic_similarity(
            claim,
            evidence,
        )
    )

    token_overlap = (
        calculate_token_overlap(
            claim,
            evidence,
        )
    )

    phrase_agreement = (
        calculate_phrase_agreement(
            claim,
            evidence,
        )
    )

    numeric_agreement = (
        calculate_numeric_agreement(
            claim,
            evidence,
        )
    )

    contradiction_indicators = (
        detect_contradiction_indicators(
            claim,
            evidence,
        )
    )

    numeric_contradiction = (
        detect_numeric_contradiction(
            claim,
            evidence,
        )
    )

    # ========================================================
    # CONTRADICTION SCORE
    # ========================================================

    contradiction_score = 0.0

    if contradiction_indicators:

        contradiction_score += 0.35

    if numeric_contradiction:

        contradiction_score += 0.30

    # Strong topic match is required before
    # treating a numeric mismatch as contradiction.

    if phrase_agreement >= 0.5:

        contradiction_score += (
            0.20
            if numeric_contradiction
            else 0.0
        )

    # ========================================================
    # SUPPORT SCORE
    # ========================================================

    support_score = (

        0.40
        * semantic_similarity

        + 0.20
        * token_overlap

        + 0.20
        * phrase_agreement

        + 0.20
        * numeric_agreement
    )

        # ========================================================
    # CLASSIFICATION
    # ========================================================

    # Explicit negation mismatch is a strong contradiction
    # when the claim and evidence discuss the same topic.

    claim_negation = contains_negation(
        claim
    )

    evidence_negation = contains_negation(
        evidence
    )

    negation_mismatch = (
        claim_negation
        != evidence_negation
    )

    if (
        negation_mismatch
        and phrase_agreement >= 0.5
        and semantic_similarity >= 0.15
    ):

        relation = "contradicts"

        contradiction_score = max(
            contradiction_score,
            0.70,
        )

    elif (
        contradiction_score >= 0.50
        and phrase_agreement >= 0.5
    ):

        relation = "contradicts"

    elif support_score >= 0.45:

        relation = "supports"

    else:

        relation = "neutral"
    # ========================================================
    # CONFIDENCE
    # ========================================================

    confidence = max(
        support_score,
        contradiction_score,
    )

    confidence = min(
        confidence,
        1.0,
    )

    return {

        "relation": relation,

        "confidence": round(
            confidence,
            4,
        ),

        "semantic_similarity": (
            semantic_similarity
        ),

        "token_overlap": (
            token_overlap
        ),

        "phrase_agreement": (
            phrase_agreement
        ),

        "numeric_agreement": (
            numeric_agreement
        ),

        "support_score": round(
            support_score,
            4,
        ),

        "contradiction_score": round(
            contradiction_score,
            4,
        ),

        "contradiction_indicators": (
            contradiction_indicators
        ),

        "numeric_contradiction": (
            numeric_contradiction
        ),
    }


# ============================================================
# DEMO EVIDENCE
# ============================================================

def build_demo_cases():

    return [

        {
            "case_id": "case_0001",

            "claim": (
                "The unemployment rate "
                "dropped to 3% in 2024."
            ),

            "evidence": (
                "The unemployment rate "
                "declined to approximately "
                "3 percent during 2024."
            ),

            "expected_relation": (
                "supports"
            ),
        },

        {
            "case_id": "case_0002",

            "claim": (
                "The unemployment rate "
                "dropped to 3% in 2024."
            ),

            "evidence": (
                "The unemployment rate "
                "was closer to 4% during "
                "the same period."
            ),

            "expected_relation": (
                "contradicts"
            ),
        },

        {
            "case_id": "case_0003",

            "claim": (
                "The unemployment rate "
                "dropped to 3% in 2024."
            ),

            "evidence": (
                "The national population "
                "increased during 2024."
            ),

            "expected_relation": (
                "neutral"
            ),
        },

        {
            "case_id": "case_0004",

            "claim": (
                "The unemployment rate "
                "did not drop to 3% in 2024."
            ),

            "evidence": (
                "The unemployment rate "
                "declined to approximately "
                "3 percent during 2024."
            ),

            "expected_relation": (
                "contradicts"
            ),
        },
    ]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "VERILENS - PHASE 7.4"
    )

    print(
        "SUPPORT / CONTRADICTION CLASSIFICATION"
    )

    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cases = build_demo_cases()

    results = []

    # ========================================================
    # PROCESS CASES
    # ========================================================

    for case in cases:

        print(
            "\n" + "-" * 70
        )

        print(
            f"CASE: {case['case_id']}"
        )

        print(
            f"\nClaim:\n"
            f"{case['claim']}"
        )

        print(
            f"\nEvidence:\n"
            f"{case['evidence']}"
        )

        classification = (
            classify_relation(
                case["claim"],
                case["evidence"],
            )
        )

        print(
            "\nCLASSIFICATION"
        )

        print(
            f"  Relation: "
            f"{classification['relation']}"
        )

        print(
            f"  Confidence: "
            f"{classification['confidence']}"
        )

        print(
            f"  Semantic similarity: "
            f"{classification['semantic_similarity']}"
        )

        print(
            f"  Token overlap: "
            f"{classification['token_overlap']}"
        )

        print(
            f"  Phrase agreement: "
            f"{classification['phrase_agreement']}"
        )

        print(
            f"  Numeric agreement: "
            f"{classification['numeric_agreement']}"
        )

        print(
            f"  Support score: "
            f"{classification['support_score']}"
        )

        print(
            f"  Contradiction score: "
            f"{classification['contradiction_score']}"
        )

        print(
            f"  Expected: "
            f"{case['expected_relation']}"
        )

        results.append(
            {
                "case_id": case[
                    "case_id"
                ],

                "claim": case[
                    "claim"
                ],

                "evidence": case[
                    "evidence"
                ],

                "expected_relation": case[
                    "expected_relation"
                ],

                "classification": (
                    classification
                ),

                "correct": (
                    classification[
                        "relation"
                    ]
                    == case[
                        "expected_relation"
                    ]
                ),
            }
        )

    # ========================================================
    # EVALUATION
    # ========================================================

    correct_count = sum(
        item["correct"]
        for item in results
    )

    total_count = len(
        results
    )

    accuracy = (
        correct_count
        / total_count
        if total_count
        else 0.0
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "PHASE 7.4 EVALUATION"
    )

    print(
        "=" * 70
    )

    print(
        f"Correct: "
        f"{correct_count}/{total_count}"
    )

    print(
        f"Prototype accuracy: "
        f"{accuracy:.4f}"
    )

    # ========================================================
    # SAVE
    # ========================================================

    output = {

        "schema_version": "1.0",

        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "method": {

            "semantic_similarity": (
                "TF-IDF cosine similarity"
            ),

            "numeric_analysis": True,

            "phrase_analysis": True,

            "negation_detection": True,

            "contradiction_indicators": True,

            "classifier_type": (
                "transparent rule-based prototype"
            ),
        },

        "cases_processed": (
            total_count
        ),

        "correct_cases": (
            correct_count
        ),

        "prototype_accuracy": round(
            accuracy,
            4,
        ),

        "results": results,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "SUPPORT / CONTRADICTION "
        "CLASSIFICATION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Saved: {OUTPUT_PATH}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()