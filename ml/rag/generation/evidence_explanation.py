import json
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

ARTIFACT_DIR = Path(
    "ml/rag/artifacts"
)

OUTPUT_FILE = (
    ARTIFACT_DIR
    / "evidence_grounded_explanation.json"
)


# ============================================================
# EVIDENCE DATA
# ============================================================

EVIDENCE = [
    {
        "evidence_id": "evidence_0001",
        "source": "National Statistics Office",
        "source_type": "government",
        "reliability": 0.8975,
        "retrieval_relevance": 0.8185,
        "relation": "supports",
        "relation_confidence": 0.92,
        "strength": 0.7762,
        "text": (
            "The unemployment rate declined to "
            "approximately 3 percent during 2024."
        ),
    },
    {
        "evidence_id": "evidence_0002",
        "source": "Annual Labor Market Review",
        "source_type": "academic",
        "reliability": 0.782,
        "retrieval_relevance": 0.8276,
        "relation": "supports",
        "relation_confidence": 0.86,
        "strength": 0.5918,
        "text": (
            "Annual unemployment remained near "
            "3.2 percent during 2024."
        ),
    },
    {
        "evidence_id": "evidence_0003",
        "source": "Daily News Report",
        "source_type": "news",
        "reliability": 0.608,
        "retrieval_relevance": 0.70,
        "relation": "contradicts",
        "relation_confidence": 0.70,
        "strength": 0.3873,
        "text": (
            "The unemployment rate was closer to "
            "4 percent during the same period."
        ),
    },
    {
        "evidence_id": "evidence_0004",
        "source": "Population Statistics",
        "source_type": "government",
        "reliability": 0.65,
        "retrieval_relevance": 0.25,
        "relation": "neutral",
        "relation_confidence": 0.61,
        "strength": 0.0991,
        "text": (
            "The national population increased "
            "during 2024."
        ),
    },
]


# ============================================================
# STRENGTH CALCULATIONS
# ============================================================

def calculate_average_strength(evidence):

    if not evidence:
        return 0.0

    return sum(
        item["strength"]
        for item in evidence
    ) / len(evidence)


def calculate_support_strength(evidence):

    supporting = [
        item
        for item in evidence
        if item["relation"] == "supports"
    ]

    return calculate_average_strength(
        supporting
    )


def calculate_contradiction_strength(evidence):

    contradicting = [
        item
        for item in evidence
        if item["relation"] == "contradicts"
    ]

    return calculate_average_strength(
        contradicting
    )


# ============================================================
# ASSESSMENT
# ============================================================

def classify_assessment(evidence):

    supporting = [
        item
        for item in evidence
        if item["relation"] == "supports"
    ]

    contradicting = [
        item
        for item in evidence
        if item["relation"] == "contradicts"
    ]

    support_strength = (
        calculate_support_strength(
            evidence
        )
    )

    contradiction_strength = (
        calculate_contradiction_strength(
            evidence
        )
    )

    if not supporting and not contradicting:
        return "insufficient_evidence"

    if supporting and not contradicting:
        return "evidence_supports"

    if contradicting and not supporting:
        return "evidence_contradicts"

    if support_strength > contradiction_strength:
        return "evidence_supports"

    if contradiction_strength > support_strength:
        return "evidence_contradicts"

    return "mixed_evidence"


# ============================================================
# GROUNDING SCORE
# ============================================================

def calculate_grounding_score(evidence):

    if not evidence:
        return 0.0

    weighted_strength = sum(
        item["strength"]
        for item in evidence
    )

    return min(
        weighted_strength / len(evidence),
        1.0,
    )


# ============================================================
# EXPLANATION GENERATOR
# ============================================================

def generate_explanation(
    claim,
    evidence,
):

    supporting = [
        item
        for item in evidence
        if item["relation"] == "supports"
    ]

    contradicting = [
        item
        for item in evidence
        if item["relation"] == "contradicts"
    ]

    neutral = [
        item
        for item in evidence
        if item["relation"] == "neutral"
    ]

    assessment = classify_assessment(
        evidence
    )

    support_strength = (
        calculate_support_strength(
            evidence
        )
    )

    contradiction_strength = (
        calculate_contradiction_strength(
            evidence
        )
    )

    grounding_score = (
        calculate_grounding_score(
            evidence
        )
    )

    # --------------------------------------------------------
    # OPENING
    # --------------------------------------------------------

    if assessment == "evidence_supports":

        opening = (
            "The available evidence generally "
            "supports the claim."
        )

    elif assessment == "evidence_contradicts":

        opening = (
            "The available evidence generally "
            "contradicts the claim."
        )

    elif assessment == "mixed_evidence":

        opening = (
            "The available evidence is mixed, "
            "with both supporting and contradicting "
            "sources."
        )

    else:

        opening = (
            "The available evidence is insufficient "
            "to establish the claim."
        )

    # --------------------------------------------------------
    # SUPPORTING EVIDENCE
    # --------------------------------------------------------

    supporting_text = []

    for item in supporting:

        supporting_text.append(
            (
                f"[{item['evidence_id']}] "
                f"{item['source']} provides "
                f"supporting evidence: "
                f"\"{item['text']}\" "
                f"(strength={item['strength']:.4f})."
            )
        )

    # --------------------------------------------------------
    # CONTRADICTING EVIDENCE
    # --------------------------------------------------------

    contradicting_text = []

    for item in contradicting:

        contradicting_text.append(
            (
                f"[{item['evidence_id']}] "
                f"{item['source']} provides "
                f"contradicting evidence: "
                f"\"{item['text']}\" "
                f"(strength={item['strength']:.4f})."
            )
        )

    # --------------------------------------------------------
    # NEUTRAL EVIDENCE
    # --------------------------------------------------------

    neutral_text = []

    for item in neutral:

        neutral_text.append(
            (
                f"[{item['evidence_id']}] "
                f"{item['source']} was retrieved "
                f"but does not directly support or "
                f"contradict the claim."
            )
        )

    # --------------------------------------------------------
    # FINAL EXPLANATION
    # --------------------------------------------------------

    explanation_parts = [
        opening,
        (
            f"The claim analyzed was: "
            f"\"{claim}\""
        ),
    ]

    if supporting_text:

        explanation_parts.append(
            "Supporting evidence: "
            + " ".join(
                supporting_text
            )
        )

    if contradicting_text:

        explanation_parts.append(
            "Contradicting evidence: "
            + " ".join(
                contradicting_text
            )
        )

    if neutral_text:

        explanation_parts.append(
            "Neutral evidence: "
            + " ".join(
                neutral_text
            )
        )

    explanation_parts.append(
        (
            f"The average supporting evidence "
            f"strength is {support_strength:.4f}, "
            f"while the average contradicting "
            f"evidence strength is "
            f"{contradiction_strength:.4f}."
        )
    )

    explanation_parts.append(
        (
            f"Overall evidence grounding score: "
            f"{grounding_score:.4f}."
        )
    )

    explanation_parts.append(
        (
            "This assessment is based only on the "
            "retrieved evidence supplied to the "
            "explanation engine and should not be "
            "treated as an independently verified "
            "fact."
        )
    )

    explanation = " ".join(
        explanation_parts
    )

    return {
        "claim": claim,
        "assessment": assessment,
        "grounding_score": round(
            grounding_score,
            4,
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
        "average_support_strength": round(
            support_strength,
            4,
        ),
        "average_contradiction_strength": round(
            contradiction_strength,
            4,
        ),
        "explanation": explanation,
        "evidence": evidence,
    }


# ============================================================
# DEMO
# ============================================================

def run_demo():

    print("=" * 70)

    print(
        "PHASE 8.2 — EVIDENCE-GROUNDED EXPLANATION"
    )

    print("=" * 70)

    claim = (
        "Did unemployment remain around "
        "three percent during 2024?"
    )

    result = generate_explanation(
        claim=claim,
        evidence=EVIDENCE,
    )

    print("\nCLAIM")
    print("-" * 70)
    print(result["claim"])

    print("\nASSESSMENT")
    print("-" * 70)
    print(result["assessment"])

    print("\nGROUNDING SCORE")
    print("-" * 70)
    print(result["grounding_score"])

    print("\nEVIDENCE COUNTS")
    print("-" * 70)

    print(
        f"Supporting: "
        f"{result['supporting_count']}"
    )

    print(
        f"Contradicting: "
        f"{result['contradicting_count']}"
    )

    print(
        f"Neutral: "
        f"{result['neutral_count']}"
    )

    print("\nEXPLANATION")
    print("-" * 70)
    print(result["explanation"])

    # --------------------------------------------------------
    # SAVE ARTIFACT
    # --------------------------------------------------------

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
        )

    print("\n" + "=" * 70)

    print(
        "PHASE 8.2 EVIDENCE-GROUNDED "
        "EXPLANATION COMPLETE"
    )

    print("=" * 70)

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_demo()