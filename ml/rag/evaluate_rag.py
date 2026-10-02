import json
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

ARTIFACT_DIR = Path(
    "ml/rag/artifacts"
)

EXPLANATION_FILE = (
    ARTIFACT_DIR
    / "evidence_grounded_explanation.json"
)

OUTPUT_FILE = (
    ARTIFACT_DIR
    / "rag_evaluation.json"
)


# ============================================================
# EVALUATION CASES
# ============================================================

CASES = [
    {
        "case_id": "rag_0001",
        "claim": (
            "Did unemployment remain around "
            "three percent during 2024?"
        ),
        "expected_assessment": "evidence_supports",
        "expected_supporting": [
            "evidence_0001",
            "evidence_0002",
        ],
        "expected_contradicting": [
            "evidence_0003",
        ],
    }
]


# ============================================================
# LOAD EXPLANATION
# ============================================================

def load_explanation():

    if not EXPLANATION_FILE.exists():

        raise FileNotFoundError(
            f"Explanation artifact not found: "
            f"{EXPLANATION_FILE}"
        )

    with open(
        EXPLANATION_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text):

    return " ".join(
        text
        .strip()
        .lower()
        .split()
    )


# ============================================================
# EVIDENCE GROUNDING
# ============================================================

def check_evidence_grounding(
    explanation,
):

    explanation_text = normalize_text(
        explanation["explanation"]
    )

    referenced_evidence = (
        explanation["evidence"]
    )

    if not referenced_evidence:
        return False

    for item in referenced_evidence:

        evidence_id = (
            item["evidence_id"]
        )

        evidence_text = normalize_text(
            item["text"]
        )

        id_present = (
            f"[{evidence_id}]"
            in explanation_text
        )

        text_present = (
            evidence_text
            in explanation_text
        )

        if not id_present:
            return False

        if not text_present:
            return False

    return True


# ============================================================
# CASE EVALUATION
# ============================================================

def evaluate_case(
    case,
    explanation,
):

    retrieved_ids = {
        item["evidence_id"]
        for item in explanation["evidence"]
    }

    supporting_ids = {
        item["evidence_id"]
        for item in explanation["evidence"]
        if item["relation"] == "supports"
    }

    contradicting_ids = {
        item["evidence_id"]
        for item in explanation["evidence"]
        if item["relation"] == "contradicts"
    }

    expected_supporting = set(
        case["expected_supporting"]
    )

    expected_contradicting = set(
        case["expected_contradicting"]
    )

    expected_relevant = (
        expected_supporting
        | expected_contradicting
    )

    retrieved_relevant = (
        retrieved_ids
        & expected_relevant
    )

    if expected_relevant:

        retrieval_recall = (
            len(retrieved_relevant)
            / len(expected_relevant)
        )

    else:

        retrieval_recall = 1.0

    if expected_supporting:

        supporting_recall = (
            len(
                supporting_ids
                & expected_supporting
            )
            / len(expected_supporting)
        )

    else:

        supporting_recall = 1.0

    if expected_contradicting:

        contradiction_recall = (
            len(
                contradicting_ids
                & expected_contradicting
            )
            / len(expected_contradicting)
        )

    else:

        contradiction_recall = 1.0

    assessment_correct = (
        explanation["assessment"]
        == case["expected_assessment"]
    )

    evidence_grounded = (
        check_evidence_grounding(
            explanation
        )
    )

    return {
        "case_id": case["case_id"],
        "retrieval_recall": round(
            retrieval_recall,
            4,
        ),
        "supporting_recall": round(
            supporting_recall,
            4,
        ),
        "contradiction_recall": round(
            contradiction_recall,
            4,
        ),
        "assessment_correct": (
            assessment_correct
        ),
        "evidence_grounded": (
            evidence_grounded
        ),
        "grounding_score": explanation[
            "grounding_score"
        ],
    }


# ============================================================
# MAIN EVALUATION
# ============================================================

def run_evaluation():

    print("=" * 70)

    print(
        "PHASE 8.3 — RAG PIPELINE EVALUATION"
    )

    print("=" * 70)

    explanation = load_explanation()

    results = []

    for case in CASES:

        result = evaluate_case(
            case,
            explanation,
        )

        results.append(
            result
        )

        print("\nCASE")
        print("-" * 70)

        print(
            result["case_id"]
        )

        print(
            f"Retrieval recall: "
            f"{result['retrieval_recall']:.4f}"
        )

        print(
            f"Supporting recall: "
            f"{result['supporting_recall']:.4f}"
        )

        print(
            f"Contradiction recall: "
            f"{result['contradiction_recall']:.4f}"
        )

        print(
            f"Assessment correct: "
            f"{result['assessment_correct']}"
        )

        print(
            f"Evidence grounded: "
            f"{result['evidence_grounded']}"
        )

        print(
            f"Grounding score: "
            f"{result['grounding_score']:.4f}"
        )

    # --------------------------------------------------------
    # AGGREGATES
    # --------------------------------------------------------

    count = len(results)

    average_retrieval = sum(
        result["retrieval_recall"]
        for result in results
    ) / count

    average_supporting = sum(
        result["supporting_recall"]
        for result in results
    ) / count

    average_contradiction = sum(
        result["contradiction_recall"]
        for result in results
    ) / count

    assessment_accuracy = sum(
        result["assessment_correct"]
        for result in results
    ) / count

    grounding_rate = sum(
        result["evidence_grounded"]
        for result in results
    ) / count

    average_grounding_score = sum(
        result["grounding_score"]
        for result in results
    ) / count

    # --------------------------------------------------------
    # OVERALL PASS
    # --------------------------------------------------------

    overall_pass = (
        average_retrieval >= 0.80
        and average_supporting >= 0.80
        and average_contradiction >= 0.80
        and assessment_accuracy >= 0.80
        and grounding_rate >= 0.80
    )

    evaluation = {
        "phase": "8.3",
        "cases_evaluated": count,
        "results": results,
        "metrics": {
            "average_retrieval_recall": round(
                average_retrieval,
                4,
            ),
            "average_supporting_recall": round(
                average_supporting,
                4,
            ),
            "average_contradiction_recall": round(
                average_contradiction,
                4,
            ),
            "assessment_accuracy": round(
                assessment_accuracy,
                4,
            ),
            "evidence_grounding_rate": round(
                grounding_rate,
                4,
            ),
            "average_grounding_score": round(
                average_grounding_score,
                4,
            ),
        },
        "overall_pass": overall_pass,
        "note": (
            "This is a prototype evaluation using "
            "synthetic demonstration evidence. "
            "It is not a statistically meaningful "
            "real-world benchmark."
        ),
    }

    # --------------------------------------------------------
    # SAVE
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
            evaluation,
            file,
            indent=2,
        )

    print("\n" + "=" * 70)

    print(
        "RAG METRICS"
    )

    print("=" * 70)

    print(
        f"Average retrieval recall: "
        f"{average_retrieval:.4f}"
    )

    print(
        f"Average supporting recall: "
        f"{average_supporting:.4f}"
    )

    print(
        f"Average contradiction recall: "
        f"{average_contradiction:.4f}"
    )

    print(
        f"Assessment accuracy: "
        f"{assessment_accuracy:.4f}"
    )

    print(
        f"Evidence grounding rate: "
        f"{grounding_rate:.4f}"
    )

    print(
        f"Average grounding score: "
        f"{average_grounding_score:.4f}"
    )

    print("\n" + "=" * 70)

    print(
        f"OVERALL RAG PIPELINE PASS: "
        f"{overall_pass}"
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
    run_evaluation()