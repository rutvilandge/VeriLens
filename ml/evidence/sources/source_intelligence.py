import json
from pathlib import Path
from datetime import datetime


# ========================================================
# CONFIGURATION
# ========================================================

ARTIFACT_DIR = Path("ml/evidence/artifacts")
OUTPUT_FILE = ARTIFACT_DIR / "source_intelligence_examples.json"


# ========================================================
# SOURCE TYPES
# ========================================================

VALID_SOURCE_TYPES = {
    "government",
    "academic",
    "news",
    "fact_check",
    "organization",
    "company",
    "unknown",
}


# ========================================================
# SOURCE CREATION
# ========================================================

def create_source(
    source_id,
    name,
    source_type,
    publication_date=None,
    reliability_score=0.5,
):
    """
    Create a normalized source intelligence record.
    """

    if source_type not in VALID_SOURCE_TYPES:
        raise ValueError(
            f"Invalid source type: {source_type}"
        )

    reliability_score = max(
        0.0,
        min(1.0, float(reliability_score)),
    )

    return {
        "source_id": source_id,
        "name": name,
        "source_type": source_type,
        "publication_date": publication_date,
        "reliability_score": round(
            reliability_score,
            4,
        ),
        "claims_analyzed": 0,
        "supporting_claims": 0,
        "contradicting_claims": 0,
        "neutral_claims": 0,
        "historical_accuracy": None,
        "created_at": datetime.utcnow().isoformat(),
    }


# ========================================================
# SOURCE PERFORMANCE
# ========================================================

def update_source_performance(
    source,
    relation,
):
    """
    Update source-level statistics after
    evaluating a claim against the source.
    """

    source["claims_analyzed"] += 1

    if relation == "supports":
        source["supporting_claims"] += 1

    elif relation == "contradicts":
        source["contradicting_claims"] += 1

    elif relation == "neutral":
        source["neutral_claims"] += 1

    else:
        raise ValueError(
            f"Invalid relation: {relation}"
        )

    return source


# ========================================================
# HISTORICAL ACCURACY
# ========================================================

def calculate_historical_accuracy(source):
    """
    Estimate historical accuracy from previously
    evaluated claims.

    Accuracy here is based on claims that received
    an externally verified outcome.

    For this prototype, verified outcomes are represented
    by the supporting_claims count.
    """

    claims = source["claims_analyzed"]

    if claims == 0:
        source["historical_accuracy"] = None
        return source

    verified_positive = source["supporting_claims"]

    accuracy = verified_positive / claims

    source["historical_accuracy"] = round(
        accuracy,
        4,
    )

    return source


# ========================================================
# SOURCE RELIABILITY UPDATE
# ========================================================

def calculate_adjusted_reliability(source):
    """
    Combine the initial reliability estimate with
    historical performance.

    Historical evidence receives greater weight only
    once the source has accumulated enough observations.
    """

    historical_accuracy = source[
        "historical_accuracy"
    ]

    base_reliability = source[
        "reliability_score"
    ]

    if historical_accuracy is None:
        return round(
            base_reliability,
            4,
        )

    claims = source[
        "claims_analyzed"
    ]

    if claims < 5:
        historical_weight = 0.20

    elif claims < 20:
        historical_weight = 0.35

    else:
        historical_weight = 0.50

    adjusted = (
        (1 - historical_weight)
        * base_reliability
        + historical_weight
        * historical_accuracy
    )

    return round(
        adjusted,
        4,
    )


# ========================================================
# SOURCE INTELLIGENCE SUMMARY
# ========================================================

def build_source_summary(source):
    """
    Produce the final source intelligence summary.
    """

    source = calculate_historical_accuracy(
        source
    )

    adjusted_reliability = (
        calculate_adjusted_reliability(
            source
        )
    )

    return {
        "source_id": source["source_id"],
        "name": source["name"],
        "source_type": source["source_type"],
        "publication_date": source[
            "publication_date"
        ],
        "reliability_score": source[
            "reliability_score"
        ],
        "adjusted_reliability": adjusted_reliability,
        "claims_analyzed": source[
            "claims_analyzed"
        ],
        "supporting_claims": source[
            "supporting_claims"
        ],
        "contradicting_claims": source[
            "contradicting_claims"
        ],
        "neutral_claims": source[
            "neutral_claims"
        ],
        "historical_accuracy": source[
            "historical_accuracy"
        ],
    }


# ========================================================
# DEMO
# ========================================================

def run_demo():

    print("=" * 70)
    print("PHASE 7.5 — SOURCE INTELLIGENCE")
    print("=" * 70)

    sources = [
        create_source(
            source_id="source_0001",
            name="National Statistics Office",
            source_type="government",
            publication_date="2024-12-31",
            reliability_score=0.95,
        ),
        create_source(
            source_id="source_0002",
            name="Annual Labor Market Review",
            source_type="academic",
            publication_date="2025-01-15",
            reliability_score=0.88,
        ),
        create_source(
            source_id="source_0003",
            name="Daily News Report",
            source_type="news",
            publication_date="2024-11-20",
            reliability_score=0.72,
        ),
    ]

    # Simulated historical claim evaluations.
    evaluations = {
        "source_0001": [
            "supports",
            "supports",
            "supports",
            "neutral",
            "supports",
        ],
        "source_0002": [
            "supports",
            "supports",
            "contradicts",
            "supports",
            "neutral",
        ],
        "source_0003": [
            "supports",
            "contradicts",
            "contradicts",
            "neutral",
            "supports",
        ],
    }

    print("\nSOURCE EVALUATIONS")
    print("-" * 70)

    for source in sources:

        relations = evaluations[
            source["source_id"]
        ]

        for relation in relations:
            update_source_performance(
                source,
                relation,
            )

        summary = build_source_summary(
            source
        )

        print(
            f"\nSource: {summary['name']}"
        )

        print(
            f"Type: {summary['source_type']}"
        )

        print(
            f"Initial reliability: "
            f"{summary['reliability_score']}"
        )

        print(
            f"Claims analyzed: "
            f"{summary['claims_analyzed']}"
        )

        print(
            f"Supporting: "
            f"{summary['supporting_claims']}"
        )

        print(
            f"Contradicting: "
            f"{summary['contradicting_claims']}"
        )

        print(
            f"Neutral: "
            f"{summary['neutral_claims']}"
        )

        print(
            f"Historical accuracy: "
            f"{summary['historical_accuracy']}"
        )

        print(
            f"Adjusted reliability: "
            f"{summary['adjusted_reliability']}"
        )

    # ====================================================
    # SAVE ARTIFACT
    # ====================================================

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "phase": "7.5",
        "name": "source_intelligence",
        "sources": [
            build_source_summary(source)
            for source in sources
        ],
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
    print("PHASE 7.5 SOURCE INTELLIGENCE COMPLETE")
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