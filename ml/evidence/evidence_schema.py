from pathlib import Path
import json
from datetime import datetime, timezone


# ============================================================
# VERILENS
# PHASE 7.2 — EVIDENCE DATA MODEL
# ============================================================

OUTPUT_DIR = Path(
    "ml/evidence/artifacts"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "evidence_schema_examples.json"
)


# ============================================================
# EVIDENCE RELATIONS
# ============================================================

VALID_RELATIONS = {
    "supports",
    "contradicts",
    "neutral",
}


# ============================================================
# SOURCE CREATION
# ============================================================

def create_source(
    source_id,
    title,
    publisher,
    url,
    publication_date=None,
    source_type="web",
):
    """
    Create a normalized evidence source.
    """

    return {
        "source_id": source_id,
        "title": title,
        "publisher": publisher,
        "url": url,
        "publication_date": publication_date,
        "source_type": source_type,
    }


# ============================================================
# EVIDENCE CREATION
# ============================================================

def create_evidence(
    evidence_id,
    claim_id,
    source,
    excerpt,
    relation,
    relevance_score,
    source_reliability,
):
    """
    Create a structured evidence object.
    """

    if relation not in VALID_RELATIONS:
        raise ValueError(
            f"Invalid evidence relation: {relation}"
        )

    if not 0 <= relevance_score <= 1:
        raise ValueError(
            "relevance_score must be between 0 and 1."
        )

    if not 0 <= source_reliability <= 1:
        raise ValueError(
            "source_reliability must be between 0 and 1."
        )

    return {
        "evidence_id": evidence_id,
        "claim_id": claim_id,

        "source": source,

        "excerpt": excerpt,

        "relation": relation,

        "relevance_score": relevance_score,

        "source_reliability": source_reliability,

        "evidence_strength": None,

    }


# ============================================================
# EVIDENCE STRENGTH
# ============================================================

def calculate_evidence_strength(
    relevance_score,
    source_reliability,
):
    """
    Initial evidence strength.

    This is intentionally simple for Phase 7.2.
    A richer scoring system comes in Phase 7.6.
    """

    strength = (
        relevance_score
        * source_reliability
    )

    return round(
        strength,
        4,
    )


# ============================================================
# CLAIM ASSESSMENT
# ============================================================

def create_claim_assessment(
    claim,
    evidence_items,
):
    """
    Aggregate evidence associated with one claim.
    """

    supporting = [
        item
        for item in evidence_items
        if item["relation"] == "supports"
    ]

    contradicting = [
        item
        for item in evidence_items
        if item["relation"] == "contradicts"
    ]

    neutral = [
        item
        for item in evidence_items
        if item["relation"] == "neutral"
    ]

    supporting_strength = sum(
        item["evidence_strength"]
        or 0
        for item in supporting
    )

    contradicting_strength = sum(
        item["evidence_strength"]
        or 0
        for item in contradicting
    )

    if (
        supporting_strength == 0
        and contradicting_strength == 0
    ):
        preliminary_assessment = (
            "insufficient_evidence"
        )

    elif (
        supporting_strength
        > contradicting_strength
    ):
        preliminary_assessment = (
            "evidence_supports"
        )

    elif (
        contradicting_strength
        > supporting_strength
    ):
        preliminary_assessment = (
            "evidence_contradicts"
        )

    else:
        preliminary_assessment = (
            "mixed_evidence"
        )

    return {
        "claim_id": claim["claim_id"],

        "claim_text": claim["claim_text"],

        "evidence_count": len(
            evidence_items
        ),

        "supporting_count": len(
            supporting
        ),

        "contradicting_count": len(
            contradicting
        ),

        "neutral_count": len(
            neutral
        ),

        "supporting_strength": round(
            supporting_strength,
            4,
        ),

        "contradicting_strength": round(
            contradicting_strength,
            4,
        ),

        "preliminary_assessment": (
            preliminary_assessment
        ),

        "status": "evidence_review",

    }


# ============================================================
# DEMO
# ============================================================

def main():

    print("=" * 70)
    print(
        "VERILENS - PHASE 7.2"
    )
    print(
        "EVIDENCE DATA MODEL"
    )
    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # CLAIM
    # ========================================================

    claim = {
        "claim_id": "claim_0001",

        "claim_text": (
            "The unemployment rate dropped "
            "to 3% in 2024."
        ),

        "claim_type": "numeric",

        "entities": [
            "Unemployment rate"
        ],

        "time_references": [
            "2024"
        ],

        "numeric_references": [
            "3%"
        ],

        "status": "unverified",
    }

    # ========================================================
    # SOURCES
    # ========================================================

    source_1 = create_source(
        source_id="source_0001",

        title=(
            "Employment Situation Summary"
        ),

        publisher="Example Statistics Bureau",

        url=(
            "https://example.org/"
            "employment-2024"
        ),

        publication_date="2024-12-01",

        source_type="official_report",
    )

    source_2 = create_source(
        source_id="source_0002",

        title=(
            "Labor Market Review 2024"
        ),

        publisher="Example Research Institute",

        url=(
            "https://example.org/"
            "labor-market-review"
        ),

        publication_date="2024-12-15",

        source_type="research_report",
    )

    source_3 = create_source(
        source_id="source_0003",

        title=(
            "Employment Rate Analysis"
        ),

        publisher="Example News Organization",

        url=(
            "https://example.org/"
            "employment-analysis"
        ),

        publication_date="2025-01-05",

        source_type="news",
    )

    # ========================================================
    # EVIDENCE
    # ========================================================

    evidence_1 = create_evidence(
        evidence_id="evidence_0001",

        claim_id="claim_0001",

        source=source_1,

        excerpt=(
            "The unemployment rate reached "
            "approximately 3% during 2024."
        ),

        relation="supports",

        relevance_score=0.94,

        source_reliability=0.95,
    )

    evidence_2 = create_evidence(
        evidence_id="evidence_0002",

        claim_id="claim_0001",

        source=source_2,

        excerpt=(
            "Annual unemployment remained "
            "near 3.2% throughout the year."
        ),

        relation="supports",

        relevance_score=0.88,

        source_reliability=0.90,
    )

    evidence_3 = create_evidence(
        evidence_id="evidence_0003",

        claim_id="claim_0001",

        source=source_3,

        excerpt=(
            "The annual unemployment rate "
            "was closer to 4%."
        ),

        relation="contradicts",

        relevance_score=0.91,

        source_reliability=0.78,
    )

    evidence_items = [
        evidence_1,
        evidence_2,
        evidence_3,
    ]

    # ========================================================
    # CALCULATE STRENGTH
    # ========================================================

    for evidence in evidence_items:

        evidence[
            "evidence_strength"
        ] = calculate_evidence_strength(
            evidence[
                "relevance_score"
            ],
            evidence[
                "source_reliability"
            ],
        )

    # ========================================================
    # ASSESSMENT
    # ========================================================

    assessment = create_claim_assessment(
        claim,
        evidence_items,
    )

    # ========================================================
    # FINAL STRUCTURE
    # ========================================================

    result = {
        "schema_version": "1.0",

        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "claim": claim,

        "evidence": evidence_items,

        "assessment": assessment,
    }

    # ========================================================
    # PRINT
    # ========================================================

    print(
        "\nCLAIM"
    )

    print(
        claim["claim_text"]
    )

    print(
        "\nEVIDENCE"
    )

    for evidence in evidence_items:

        print(
            f"\n{evidence['evidence_id']}"
        )

        print(
            f"  Relation: "
            f"{evidence['relation']}"
        )

        print(
            f"  Relevance: "
            f"{evidence['relevance_score']}"
        )

        print(
            f"  Reliability: "
            f"{evidence['source_reliability']}"
        )

        print(
            f"  Strength: "
            f"{evidence['evidence_strength']}"
        )

    print(
        "\nASSESSMENT"
    )

    print(
        f"Supporting: "
        f"{assessment['supporting_count']}"
    )

    print(
        f"Contradicting: "
        f"{assessment['contradicting_count']}"
    )

    print(
        f"Neutral: "
        f"{assessment['neutral_count']}"
    )

    print(
        f"Assessment: "
        f"{assessment['preliminary_assessment']}"
    )

    # ========================================================
    # SAVE
    # ========================================================

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\n" + "=" * 70
    )

    print(
        "EVIDENCE DATA MODEL COMPLETE"
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