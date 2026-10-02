import json
from pathlib import Path


# ========================================================
# CONFIGURATION
# ========================================================

ARTIFACT_DIR = Path("ml/evidence/artifacts")

OUTPUT_FILE = (
    ARTIFACT_DIR
    / "evidence_graph_examples.json"
)


# ========================================================
# GRAPH NODE CREATION
# ========================================================

def create_claim_node(
    claim_id,
    claim,
):
    """
    Create a claim node.
    """

    return {
        "node_id": claim_id,
        "node_type": "claim",
        "label": claim,
    }


def create_evidence_node(
    evidence_id,
    excerpt,
    relation,
    strength,
):
    """
    Create an evidence node.
    """

    return {
        "node_id": evidence_id,
        "node_type": "evidence",
        "label": excerpt,
        "relation": relation,
        "evidence_strength": round(
            strength,
            4,
        ),
    }


def create_source_node(
    source_id,
    source_name,
    source_type,
    reliability,
):
    """
    Create a source node.
    """

    return {
        "node_id": source_id,
        "node_type": "source",
        "label": source_name,
        "source_type": source_type,
        "reliability": round(
            reliability,
            4,
        ),
    }


# ========================================================
# GRAPH EDGE CREATION
# ========================================================

def create_edge(
    source,
    target,
    relation,
    weight=None,
):
    """
    Create a directed graph relationship.
    """

    edge = {
        "source": source,
        "target": target,
        "relation": relation,
    }

    if weight is not None:
        edge["weight"] = round(
            weight,
            4,
        )

    return edge


# ========================================================
# GRAPH CONSTRUCTION
# ========================================================

def build_evidence_graph(
    claim,
    evidence_records,
):
    """
    Construct a claim-evidence-source graph.

    Structure:

        CLAIM
          |
          +---- SUPPORTS ----> EVIDENCE
          |                       |
          |                       +---- FROM ----> SOURCE
          |
          +---- CONTRADICTS --> EVIDENCE
                                  |
                                  +---- FROM ----> SOURCE
    """

    nodes = []
    edges = []

    # ----------------------------------------------------
    # Claim node
    # ----------------------------------------------------

    claim_id = "claim_0001"

    claim_node = create_claim_node(
        claim_id,
        claim,
    )

    nodes.append(
        claim_node
    )

    # ----------------------------------------------------
    # Evidence and source nodes
    # ----------------------------------------------------

    for record in evidence_records:

        evidence_id = record[
            "evidence_id"
        ]

        source_id = record[
            "source_id"
        ]

        evidence_node = create_evidence_node(
            evidence_id=evidence_id,
            excerpt=record["excerpt"],
            relation=record["relation"],
            strength=record[
                "evidence_strength"
            ],
        )

        source_node = create_source_node(
            source_id=source_id,
            source_name=record[
                "source_name"
            ],
            source_type=record[
                "source_type"
            ],
            reliability=record[
                "source_reliability"
            ],
        )

        nodes.append(
            evidence_node
        )

        nodes.append(
            source_node
        )

        # ------------------------------------------------
        # Claim -> Evidence
        # ------------------------------------------------

        claim_edge = create_edge(
            source=claim_id,
            target=evidence_id,
            relation=record[
                "relation"
            ],
            weight=record[
                "evidence_strength"
            ],
        )

        edges.append(
            claim_edge
        )

        # ------------------------------------------------
        # Evidence -> Source
        # ------------------------------------------------

        source_edge = create_edge(
            source=evidence_id,
            target=source_id,
            relation="from_source",
        )

        edges.append(
            source_edge
        )

    return {
        "nodes": nodes,
        "edges": edges,
    }


# ========================================================
# GRAPH STATISTICS
# ========================================================

def calculate_graph_statistics(
    graph,
):
    """
    Calculate basic graph-level statistics.
    """

    nodes = graph["nodes"]
    edges = graph["edges"]

    claim_nodes = [
        node
        for node in nodes
        if node["node_type"] == "claim"
    ]

    evidence_nodes = [
        node
        for node in nodes
        if node["node_type"] == "evidence"
    ]

    source_nodes = [
        node
        for node in nodes
        if node["node_type"] == "source"
    ]

    supporting_edges = [
        edge
        for edge in edges
        if edge["relation"] == "supports"
    ]

    contradicting_edges = [
        edge
        for edge in edges
        if edge["relation"] == "contradicts"
    ]

    neutral_edges = [
        edge
        for edge in edges
        if edge["relation"] == "neutral"
    ]

    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "claim_nodes": len(
            claim_nodes
        ),
        "evidence_nodes": len(
            evidence_nodes
        ),
        "source_nodes": len(
            source_nodes
        ),
        "supporting_relationships": len(
            supporting_edges
        ),
        "contradicting_relationships": len(
            contradicting_edges
        ),
        "neutral_relationships": len(
            neutral_edges
        ),
    }


# ========================================================
# GRAPH ANALYSIS
# ========================================================

def analyze_claim_graph(
    graph,
):
    """
    Produce a claim-level evidence summary.
    """

    evidence_nodes = [
        node
        for node in graph["nodes"]
        if node["node_type"] == "evidence"
    ]

    supporting = [
        node
        for node in evidence_nodes
        if node["relation"] == "supports"
    ]

    contradicting = [
        node
        for node in evidence_nodes
        if node["relation"] == "contradicts"
    ]

    neutral = [
        node
        for node in evidence_nodes
        if node["relation"] == "neutral"
    ]

    strongest_support = (
        max(
            supporting,
            key=lambda node:
                node["evidence_strength"],
        )
        if supporting
        else None
    )

    strongest_contradiction = (
        max(
            contradicting,
            key=lambda node:
                node["evidence_strength"],
        )
        if contradicting
        else None
    )

    return {
        "supporting_evidence": len(
            supporting
        ),
        "contradicting_evidence": len(
            contradicting
        ),
        "neutral_evidence": len(
            neutral
        ),
        "strongest_support": (
            strongest_support["node_id"]
            if strongest_support
            else None
        ),
        "strongest_contradiction": (
            strongest_contradiction[
                "node_id"
            ]
            if strongest_contradiction
            else None
        ),
    }


# ========================================================
# DEMO
# ========================================================

def run_demo():

    print("=" * 70)
    print("PHASE 7.7 — EVIDENCE GRAPH CONSTRUCTION")
    print("=" * 70)

    claim = (
        "The unemployment rate dropped "
        "to 3% in 2024."
    )

    evidence_records = [

        {
            "evidence_id": "evidence_0001",
            "source_id": "source_0001",
            "source_name": (
                "National Statistics Office"
            ),
            "source_type": "government",
            "source_reliability": 0.8975,
            "relation": "supports",
            "evidence_strength": 0.7762,
            "excerpt": (
                "The unemployment rate "
                "declined to approximately "
                "3 percent during 2024."
            ),
        },

        {
            "evidence_id": "evidence_0002",
            "source_id": "source_0002",
            "source_name": (
                "Annual Labor Market Review"
            ),
            "source_type": "academic",
            "source_reliability": 0.782,
            "relation": "supports",
            "evidence_strength": 0.5918,
            "excerpt": (
                "Annual unemployment remained "
                "near 3.2 percent during 2024."
            ),
        },

        {
            "evidence_id": "evidence_0003",
            "source_id": "source_0003",
            "source_name": (
                "Daily News Report"
            ),
            "source_type": "news",
            "source_reliability": 0.608,
            "relation": "contradicts",
            "evidence_strength": 0.3873,
            "excerpt": (
                "The unemployment rate was "
                "closer to 4 percent during "
                "the same period."
            ),
        },

        {
            "evidence_id": "evidence_0004",
            "source_id": "source_0004",
            "source_name": (
                "Population Statistics"
            ),
            "source_type": "government",
            "source_reliability": 0.65,
            "relation": "neutral",
            "evidence_strength": 0.0991,
            "excerpt": (
                "The national population "
                "increased during 2024."
            ),
        },
    ]

    # ----------------------------------------------------
    # BUILD GRAPH
    # ----------------------------------------------------

    graph = build_evidence_graph(
        claim=claim,
        evidence_records=evidence_records,
    )

    # ----------------------------------------------------
    # GRAPH STATISTICS
    # ----------------------------------------------------

    statistics = calculate_graph_statistics(
        graph
    )

    analysis = analyze_claim_graph(
        graph
    )

    # ----------------------------------------------------
    # DISPLAY
    # ----------------------------------------------------

    print("\nGRAPH STRUCTURE")
    print("-" * 70)

    print(
        f"Total nodes: "
        f"{statistics['total_nodes']}"
    )

    print(
        f"Total edges: "
        f"{statistics['total_edges']}"
    )

    print(
        f"Claim nodes: "
        f"{statistics['claim_nodes']}"
    )

    print(
        f"Evidence nodes: "
        f"{statistics['evidence_nodes']}"
    )

    print(
        f"Source nodes: "
        f"{statistics['source_nodes']}"
    )

    print(
        f"Supporting relationships: "
        f"{statistics['supporting_relationships']}"
    )

    print(
        f"Contradicting relationships: "
        f"{statistics['contradicting_relationships']}"
    )

    print(
        f"Neutral relationships: "
        f"{statistics['neutral_relationships']}"
    )

    # ----------------------------------------------------
    # RELATIONSHIPS
    # ----------------------------------------------------

    print("\nRELATIONSHIPS")
    print("-" * 70)

    for edge in graph["edges"]:

        if edge["relation"] in {
            "supports",
            "contradicts",
            "neutral",
        }:

            print(
                f"{edge['source']} "
                f"--{edge['relation']}--> "
                f"{edge['target']} "
                f"[weight={edge.get('weight', 'N/A')}]"
            )

        else:

            print(
                f"{edge['source']} "
                f"--{edge['relation']}--> "
                f"{edge['target']}"
            )

    # ----------------------------------------------------
    # CLAIM ANALYSIS
    # ----------------------------------------------------

    print("\nCLAIM GRAPH ANALYSIS")
    print("-" * 70)

    print(
        f"Supporting evidence: "
        f"{analysis['supporting_evidence']}"
    )

    print(
        f"Contradicting evidence: "
        f"{analysis['contradicting_evidence']}"
    )

    print(
        f"Neutral evidence: "
        f"{analysis['neutral_evidence']}"
    )

    print(
        f"Strongest support: "
        f"{analysis['strongest_support']}"
    )

    print(
        f"Strongest contradiction: "
        f"{analysis['strongest_contradiction']}"
    )

    # ====================================================
    # SAVE ARTIFACT
    # ====================================================

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "phase": "7.7",
        "name": "evidence_graph",
        "claim": claim,
        "graph": graph,
        "statistics": statistics,
        "analysis": analysis,
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
    print("PHASE 7.7 EVIDENCE GRAPH COMPLETE")
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