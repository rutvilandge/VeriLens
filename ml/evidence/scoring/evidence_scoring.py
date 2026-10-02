import json
from pathlib import Path


# ========================================================
# CONFIGURATION
# ========================================================

ARTIFACT_DIR = Path("ml/evidence/artifacts")

OUTPUT_FILE = (
    ARTIFACT_DIR
    / "evidence_scoring_examples.json"
)


# ========================================================
# SCORE COMPONENTS
# ========================================================

def calculate_evidence_strength(
    retrieval_relevance,
    source_reliability,
    relation_confidence,
):
    """
    Calculate evidence strength from three
    independent evidence signals.

    Formula:

        strength =
            retrieval relevance
            × source reliability
            × relation confidence
    """

    retrieval_relevance = max(
        0.0,
        min(1.0, float(retrieval_relevance)),
    )

    source_reliability = max(
        0.0,
        min(1.0, float(source_reliability)),
    )

    relation_confidence = max(
        0.0,
        min(1.0, float(relation_confidence)),
    )

    strength = (
        retrieval_relevance
        * source_reliability
        * relation_confidence
    )

    return round(
        strength,
        4,
    )


# ========================================================
# STRENGTH CATEGORY
# ========================================================

def classify_strength(score):
    """
    Convert the numerical evidence score
    into an interpretable category.
    """

    if score >= 0.80:
        return "very_strong"

    if score >= 0.60:
        return "strong"

    if score >= 0.40:
        return "moderate"

    if score >= 0.20:
        return "weak"

    return "very_weak"


# ========================================================
# EVIDENCE SCORE RECORD
# ========================================================

def create_evidence_score(
    evidence_id,
    claim,
    source_name,
    relation,
    retrieval_relevance,
    source_reliability,
    relation_confidence,
):
    """
    Create a complete evidence scoring record.
    """

    strength = calculate_evidence_strength(
        retrieval_relevance,
        source_reliability,
        relation_confidence,
    )

    category = classify_strength(
        strength
    )

    return {
        "evidence_id": evidence_id,
        "claim": claim,
        "source": source_name,
        "relation": relation,
        "retrieval_relevance": round(
            retrieval_relevance,
            4,
        ),
        "source_reliability": round(
            source_reliability,
            4,
        ),
        "relation_confidence": round(
            relation_confidence,
            4,
        ),
        "evidence_strength": strength,
        "strength_category": category,
    }


# ========================================================
# CLAIM-LEVEL EVIDENCE SUMMARY
# ========================================================

def summarize_claim_evidence(
    evidence_records,
):
    """
    Aggregate evidence scores for one claim.
    """

    if not evidence_records:
        return {
            "evidence_count": 0,
            "supporting_count": 0,
            "contradicting_count": 0,
            "neutral_count": 0,
            "average_strength": 0.0,
            "strongest_supporting_evidence": None,
            "strongest_contradicting_evidence": None,
        }

    supporting = [
        record
        for record in evidence_records
        if record["relation"] == "supports"
    ]

    contradicting = [
        record
        for record in evidence_records
        if record["relation"] == "contradicts"
    ]

    neutral = [
        record
        for record in evidence_records
        if record["relation"] == "neutral"
    ]

    average_strength = sum(
        record["evidence_strength"]
        for record in evidence_records
    ) / len(evidence_records)

    strongest_supporting = (
        max(
            supporting,
            key=lambda record:
                record["evidence_strength"],
        )
        if supporting
        else None
    )

    strongest_contradicting = (
        max(
            contradicting,
            key=lambda record:
                record["evidence_strength"],
        )
        if contradicting
        else None
    )

    return {
        "evidence_count": len(
            evidence_records
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
        "average_strength": round(
            average_strength,
            4,
        ),
        "strongest_supporting_evidence": (
            strongest_supporting
        ),
        "strongest_contradicting_evidence": (
            strongest_contradicting
        ),
    }


# ========================================================
# DEMO
# ========================================================

def run_demo():

    print("=" * 70)
    print("PHASE 7.6 — EVIDENCE SCORING")
    print("=" * 70)

    claim = (
        "The unemployment rate dropped "
        "to 3% in 2024."
    )

    evidence_records = [

        create_evidence_score(
            evidence_id="evidence_0001",
            claim=claim,
            source_name="National Statistics Office",
            relation="supports",
            retrieval_relevance=0.94,
            source_reliability=0.8975,
            relation_confidence=0.92,
        ),

        create_evidence_score(
            evidence_id="evidence_0002",
            claim=claim,
            source_name="Annual Labor Market Review",
            relation="supports",
            retrieval_relevance=0.88,
            source_reliability=0.782,
            relation_confidence=0.86,
        ),

        create_evidence_score(
            evidence_id="evidence_0003",
            claim=claim,
            source_name="Daily News Report",
            relation="contradicts",
            retrieval_relevance=0.91,
            source_reliability=0.608,
            relation_confidence=0.70,
        ),

        create_evidence_score(
            evidence_id="evidence_0004",
            claim=claim,
            source_name="Population Statistics",
            relation="neutral",
            retrieval_relevance=0.25,
            source_reliability=0.65,
            relation_confidence=0.61,
        ),
    ]

    # ====================================================
    # DISPLAY INDIVIDUAL SCORES
    # ====================================================

    print("\nINDIVIDUAL EVIDENCE SCORES")
    print("-" * 70)

    for record in evidence_records:

        print(
            f"\nEvidence: "
            f"{record['evidence_id']}"
        )

        print(
            f"Source: "
            f"{record['source']}"
        )

        print(
            f"Relation: "
            f"{record['relation']}"
        )

        print(
            f"Retrieval relevance: "
            f"{record['retrieval_relevance']}"
        )

        print(
            f"Source reliability: "
            f"{record['source_reliability']}"
        )

        print(
            f"Relation confidence: "
            f"{record['relation_confidence']}"
        )

        print(
            f"Evidence strength: "
            f"{record['evidence_strength']}"
        )

        print(
            f"Category: "
            f"{record['strength_category']}"
        )

    # ====================================================
    # CLAIM SUMMARY
    # ====================================================

    summary = summarize_claim_evidence(
        evidence_records
    )

    print("\n" + "=" * 70)
    print("CLAIM-LEVEL EVIDENCE SUMMARY")
    print("=" * 70)

    print(
        f"Evidence count: "
        f"{summary['evidence_count']}"
    )

    print(
        f"Supporting: "
        f"{summary['supporting_count']}"
    )

    print(
        f"Contradicting: "
        f"{summary['contradicting_count']}"
    )

    print(
        f"Neutral: "
        f"{summary['neutral_count']}"
    )

    print(
        f"Average strength: "
        f"{summary['average_strength']}"
    )

    if summary[
        "strongest_supporting_evidence"
    ]:

        strongest = summary[
            "strongest_supporting_evidence"
        ]

        print(
            "\nStrongest supporting evidence:"
        )

        print(
            f"  {strongest['evidence_id']}"
        )

        print(
            f"  Strength: "
            f"{strongest['evidence_strength']}"
        )

    if summary[
        "strongest_contradicting_evidence"
    ]:

        strongest = summary[
            "strongest_contradicting_evidence"
        ]

        print(
            "\nStrongest contradicting evidence:"
        )

        print(
            f"  {strongest['evidence_id']}"
        )

        print(
            f"  Strength: "
            f"{strongest['evidence_strength']}"
        )

    # ====================================================
    # SAVE ARTIFACT
    # ====================================================

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "phase": "7.6",
        "name": "evidence_scoring",
        "scoring_formula": (
            "retrieval_relevance "
            "* source_reliability "
            "* relation_confidence"
        ),
        "strength_thresholds": {
            "very_strong": ">= 0.80",
            "strong": ">= 0.60",
            "moderate": ">= 0.40",
            "weak": ">= 0.20",
            "very_weak": "< 0.20",
        },
        "claim": claim,
        "evidence": evidence_records,
        "summary": summary,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
        )

    print("\n" + "=" * 70)
    print("PHASE 7.6 EVIDENCE SCORING COMPLETE")
    print("=" * 70)

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print("=" * 70)


# ========================================================
# ENTRY POINT
# ========================================================

if __name__ == "__main__":
    run_demo()