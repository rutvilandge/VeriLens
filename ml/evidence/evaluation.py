import json
from pathlib import Path


# ========================================================
# CONFIGURATION
# ========================================================

ARTIFACT_DIR = Path("ml/evidence/artifacts")

OUTPUT_FILE = (
    ARTIFACT_DIR
    / "evidence_intelligence_evaluation.json"
)


# ========================================================
# EXPECTED RELATIONS
# ========================================================

RELATION_LABELS = {
    "supports",
    "contradicts",
    "neutral",
}


# ========================================================
# RELATION EVALUATION
# ========================================================

def evaluate_relations(cases):
    """
    Evaluate support / contradiction / neutral
    classification against expected labels.
    """

    correct = 0

    for case in cases:

        if (
            case["predicted_relation"]
            == case["expected_relation"]
        ):
            correct += 1

    total = len(cases)

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    return {
        "correct": correct,
        "total": total,
        "accuracy": round(
            accuracy,
            4,
        ),
    }


# ========================================================
# RETRIEVAL EVALUATION
# ========================================================

def evaluate_retrieval(cases):
    """
    Measure whether the expected evidence appears
    within the retrieved ranking.
    """

    hits = 0

    reciprocal_ranks = []

    for case in cases:

        expected_id = case[
            "expected_evidence_id"
        ]

        ranked_ids = case[
            "ranked_evidence_ids"
        ]

        if expected_id in ranked_ids:

            rank = (
                ranked_ids.index(
                    expected_id
                )
                + 1
            )

            hits += 1

            reciprocal_ranks.append(
                1 / rank
            )

        else:

            reciprocal_ranks.append(
                0.0
            )

    total = len(cases)

    hit_rate = (
        hits / total
        if total
        else 0.0
    )

    mean_reciprocal_rank = (
        sum(reciprocal_ranks)
        / len(reciprocal_ranks)
        if reciprocal_ranks
        else 0.0
    )

    return {
        "retrieval_hits": hits,
        "total_queries": total,
        "hit_rate": round(
            hit_rate,
            4,
        ),
        "mean_reciprocal_rank": round(
            mean_reciprocal_rank,
            4,
        ),
    }


# ========================================================
# EVIDENCE STRENGTH EVALUATION
# ========================================================

def evaluate_evidence_strength(
    evidence_records,
):
    """
    Summarize the distribution of evidence
    strength categories.
    """

    categories = {
        "very_strong": 0,
        "strong": 0,
        "moderate": 0,
        "weak": 0,
        "very_weak": 0,
    }

    strengths = []

    for record in evidence_records:

        category = record[
            "strength_category"
        ]

        if category in categories:
            categories[
                category
            ] += 1

        strengths.append(
            record[
                "evidence_strength"
            ]
        )

    average_strength = (
        sum(strengths)
        / len(strengths)
        if strengths
        else 0.0
    )

    return {
        "category_distribution": categories,
        "average_strength": round(
            average_strength,
            4,
        ),
    }


# ========================================================
# GRAPH EVALUATION
# ========================================================

def evaluate_graph(
    statistics,
    analysis,
):
    """
    Validate basic graph consistency.
    """

    expected_nodes = (
        statistics["claim_nodes"]
        + statistics["evidence_nodes"]
        + statistics["source_nodes"]
    )

    node_count_valid = (
        statistics["total_nodes"]
        == expected_nodes
    )

    expected_relationships = (
        statistics[
            "supporting_relationships"
        ]
        + statistics[
            "contradicting_relationships"
        ]
        + statistics[
            "neutral_relationships"
        ]
    )

    relation_count_valid = (
        expected_relationships
        == (
            statistics["evidence_nodes"]
        )
    )

    strongest_support_exists = (
        analysis[
            "strongest_support"
        ]
        is not None
    )

    strongest_contradiction_exists = (
        analysis[
            "strongest_contradiction"
        ]
        is not None
    )

    return {
        "node_count_valid":
            node_count_valid,

        "relationship_count_valid":
            relation_count_valid,

        "strongest_support_found":
            strongest_support_exists,

        "strongest_contradiction_found":
            strongest_contradiction_exists,

        "graph_consistent": all([
            node_count_valid,
            relation_count_valid,
            strongest_support_exists,
            strongest_contradiction_exists,
        ]),
    }


# ========================================================
# FINAL ASSESSMENT
# ========================================================

def determine_final_assessment(
    supporting_strength,
    contradicting_strength,
):
    """
    Produce a transparent claim-level assessment.

    This is a prototype aggregation rule.
    """

    difference = (
        supporting_strength
        - contradicting_strength
    )

    if (
        supporting_strength == 0
        and contradicting_strength == 0
    ):
        return "insufficient_evidence"

    if difference >= 0.20:
        return "evidence_supports"

    if difference <= -0.20:
        return "evidence_contradicts"

    return "mixed_evidence"


# ========================================================
# DEMO
# ========================================================

def run_evaluation():

    print("=" * 70)
    print(
        "PHASE 7.8 — EVIDENCE INTELLIGENCE EVALUATION"
    )
    print("=" * 70)

    # ----------------------------------------------------
    # Relation evaluation
    # ----------------------------------------------------

    relation_cases = [

        {
            "case_id": "case_0001",
            "predicted_relation": "supports",
            "expected_relation": "supports",
        },

        {
            "case_id": "case_0002",
            "predicted_relation": "contradicts",
            "expected_relation": "contradicts",
        },

        {
            "case_id": "case_0003",
            "predicted_relation": "neutral",
            "expected_relation": "neutral",
        },

        {
            "case_id": "case_0004",
            "predicted_relation": "contradicts",
            "expected_relation": "contradicts",
        },
    ]

    relation_results = evaluate_relations(
        relation_cases
    )

    # ----------------------------------------------------
    # Retrieval evaluation
    # ----------------------------------------------------

    retrieval_cases = [

        {
            "query_id": "claim_0001",
            "expected_evidence_id":
                "evidence_0001",

            "ranked_evidence_ids": [
                "evidence_0001",
                "evidence_0002",
                "evidence_0003",
            ],
        },

        {
            "query_id": "claim_0002",
            "expected_evidence_id":
                "evidence_0002",

            "ranked_evidence_ids": [
                "evidence_0002",
                "evidence_0001",
                "evidence_0003",
            ],
        },

        {
            "query_id": "claim_0003",
            "expected_evidence_id":
                "evidence_0003",

            "ranked_evidence_ids": [
                "evidence_0003",
                "evidence_0001",
                "evidence_0002",
            ],
        },
    ]

    retrieval_results = evaluate_retrieval(
        retrieval_cases
    )

    # ----------------------------------------------------
    # Evidence strength evaluation
    # ----------------------------------------------------

    evidence_records = [

        {
            "evidence_id": "evidence_0001",
            "relation": "supports",
            "evidence_strength": 0.7762,
            "strength_category": "strong",
        },

        {
            "evidence_id": "evidence_0002",
            "relation": "supports",
            "evidence_strength": 0.5918,
            "strength_category": "moderate",
        },

        {
            "evidence_id": "evidence_0003",
            "relation": "contradicts",
            "evidence_strength": 0.3873,
            "strength_category": "weak",
        },

        {
            "evidence_id": "evidence_0004",
            "relation": "neutral",
            "evidence_strength": 0.0991,
            "strength_category": "very_weak",
        },
    ]

    strength_results = (
        evaluate_evidence_strength(
            evidence_records
        )
    )

    # ----------------------------------------------------
    # Graph evaluation
    # ----------------------------------------------------

    graph_statistics = {
        "total_nodes": 9,
        "total_edges": 8,
        "claim_nodes": 1,
        "evidence_nodes": 4,
        "source_nodes": 4,
        "supporting_relationships": 2,
        "contradicting_relationships": 1,
        "neutral_relationships": 1,
    }

    graph_analysis = {
        "strongest_support":
            "evidence_0001",

        "strongest_contradiction":
            "evidence_0003",
    }

    graph_results = evaluate_graph(
        graph_statistics,
        graph_analysis,
    )

    # ----------------------------------------------------
    # Final claim assessment
    # ----------------------------------------------------

    supporting_strength = (
        0.7762 + 0.5918
    ) / 2

    contradicting_strength = 0.3873

    final_assessment = (
        determine_final_assessment(
            supporting_strength,
            contradicting_strength,
        )
    )

    # ----------------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------------

    print("\nRELATION CLASSIFICATION")
    print("-" * 70)

    print(
        f"Correct: "
        f"{relation_results['correct']}/"
        f"{relation_results['total']}"
    )

    print(
        f"Accuracy: "
        f"{relation_results['accuracy']}"
    )

    print("\nEVIDENCE RETRIEVAL")
    print("-" * 70)

    print(
        f"Retrieval hits: "
        f"{retrieval_results['retrieval_hits']}/"
        f"{retrieval_results['total_queries']}"
    )

    print(
        f"Hit rate: "
        f"{retrieval_results['hit_rate']}"
    )

    print(
        f"Mean Reciprocal Rank: "
        f"{retrieval_results['mean_reciprocal_rank']}"
    )

    print("\nEVIDENCE STRENGTH")
    print("-" * 70)

    print(
        f"Average strength: "
        f"{strength_results['average_strength']}"
    )

    for (
        category,
        count,
    ) in strength_results[
        "category_distribution"
    ].items():

        print(
            f"{category}: {count}"
        )

    print("\nGRAPH CONSISTENCY")
    print("-" * 70)

    print(
        f"Graph consistent: "
        f"{graph_results['graph_consistent']}"
    )

    print(
        f"Node count valid: "
        f"{graph_results['node_count_valid']}"
    )

    print(
        f"Relationship count valid: "
        f"{graph_results['relationship_count_valid']}"
    )

    print(
        f"Strongest support found: "
        f"{graph_results['strongest_support_found']}"
    )

    print(
        f"Strongest contradiction found: "
        f"{graph_results['strongest_contradiction_found']}"
    )

    print("\nFINAL CLAIM ASSESSMENT")
    print("-" * 70)

    print(
        f"Average supporting strength: "
        f"{supporting_strength:.4f}"
    )

    print(
        f"Strongest contradiction strength: "
        f"{contradicting_strength:.4f}"
    )

    print(
        f"Assessment: "
        f"{final_assessment}"
    )

    # ----------------------------------------------------
    # Overall status
    # ----------------------------------------------------

    pipeline_passed = all([
        relation_results["accuracy"] >= 0.75,
        retrieval_results["hit_rate"] >= 0.75,
        graph_results["graph_consistent"],
        final_assessment
        != "insufficient_evidence",
    ])

    print("\n" + "=" * 70)
    print("OVERALL EVIDENCE PIPELINE")
    print("=" * 70)

    print(
        f"Pipeline evaluation passed: "
        f"{pipeline_passed}"
    )

    # ----------------------------------------------------
    # SAVE ARTIFACT
    # ----------------------------------------------------

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "phase": "7.8",
        "name":
            "evidence_intelligence_evaluation",

        "relation_classification":
            relation_results,

        "retrieval":
            retrieval_results,

        "evidence_strength":
            strength_results,

        "graph":
            graph_results,

        "final_claim_assessment": {
            "average_supporting_strength":
                round(
                    supporting_strength,
                    4,
                ),

            "contradicting_strength":
                round(
                    contradicting_strength,
                    4,
                ),

            "assessment":
                final_assessment,
        },

        "pipeline_passed":
            pipeline_passed,
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
    print(
        "PHASE 7.8 EVIDENCE INTELLIGENCE "
        "EVALUATION COMPLETE"
    )
    print("=" * 70)

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print("=" * 70)


# ========================================================
# ENTRY POINT
# ========================================================

if __name__ == "__main__":
    run_evaluation()