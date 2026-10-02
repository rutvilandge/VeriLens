import json
from pathlib import Path

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


# ========================================================
# CONFIGURATION
# ========================================================

ARTIFACT_DIR = Path(
    "ml/rag/artifacts"
)

INDEX_FILE = (
    ARTIFACT_DIR
    / "evidence_faiss.index"
)

METADATA_FILE = (
    ARTIFACT_DIR
    / "evidence_faiss_metadata.json"
)

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ========================================================
# DEMO EVIDENCE CORPUS
# ========================================================

EVIDENCE_CORPUS = [

    {
        "evidence_id": "evidence_0001",
        "source": "National Statistics Office",
        "source_type": "government",
        "reliability": 0.8975,
        "text": (
            "The unemployment rate declined "
            "to approximately 3 percent "
            "during 2024."
        ),
    },

    {
        "evidence_id": "evidence_0002",
        "source": "Annual Labor Market Review",
        "source_type": "academic",
        "reliability": 0.782,
        "text": (
            "Annual unemployment remained "
            "near 3.2 percent during 2024."
        ),
    },

    {
        "evidence_id": "evidence_0003",
        "source": "Daily News Report",
        "source_type": "news",
        "reliability": 0.608,
        "text": (
            "The unemployment rate was "
            "closer to 4 percent during "
            "the same period."
        ),
    },

    {
        "evidence_id": "evidence_0004",
        "source": "Population Statistics",
        "source_type": "government",
        "reliability": 0.65,
        "text": (
            "The national population "
            "increased during 2024."
        ),
    },

    {
        "evidence_id": "evidence_0005",
        "source": "Economic Outlook Report",
        "source_type": "academic",
        "reliability": 0.84,
        "text": (
            "Labor market conditions improved "
            "throughout the second half of "
            "2024, with unemployment remaining "
            "around three percent."
        ),
    },
]


# ========================================================
# EMBEDDING MODEL
# ========================================================

def load_embedding_model():

    print(
        f"\nLoading embedding model: "
        f"{MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Embedding model loaded."
    )

    return model


# ========================================================
# CREATE EMBEDDINGS
# ========================================================

def create_embeddings(
    model,
    documents,
):

    texts = [
        document["text"]
        for document in documents
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    embeddings = embeddings.astype(
        np.float32
    )

    return embeddings


# ========================================================
# BUILD FAISS INDEX
# ========================================================

def build_faiss_index(
    embeddings,
):

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    return index


# ========================================================
# SAVE INDEX
# ========================================================

def save_index(
    index,
    documents,
):

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    faiss.write_index(
        index,
        str(INDEX_FILE),
    )

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            documents,
            file,
            indent=2,
        )

    print(
        f"\nFAISS index saved: "
        f"{INDEX_FILE}"
    )

    print(
        f"Metadata saved: "
        f"{METADATA_FILE}"
    )


# ========================================================
# SEARCH
# ========================================================

def search_evidence(
    model,
    index,
    documents,
    query,
    top_k=3,
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_embedding = (
        query_embedding.astype(
            np.float32
        )
    )

    scores, indices = index.search(
        query_embedding,
        top_k,
    )

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0],
    ):

        if index_id < 0:
            continue

        document = documents[
            int(index_id)
        ]

        results.append(
            {
                "rank": len(results) + 1,
                "evidence_id": document[
                    "evidence_id"
                ],
                "source": document[
                    "source"
                ],
                "source_type": document[
                    "source_type"
                ],
                "reliability": document[
                    "reliability"
                ],
                "similarity": round(
                    float(score),
                    4,
                ),
                "text": document[
                    "text"
                ],
            }
        )

    return results


# ========================================================
# DEMO
# ========================================================

def run_demo():

    print("=" * 70)
    print(
        "PHASE 8.1 — LOCAL SEMANTIC EVIDENCE RETRIEVAL"
    )
    print("=" * 70)

    model = load_embedding_model()

    print(
        f"\nCorpus documents: "
        f"{len(EVIDENCE_CORPUS)}"
    )

    embeddings = create_embeddings(
        model,
        EVIDENCE_CORPUS,
    )

    print(
        f"Embedding shape: "
        f"{embeddings.shape}"
    )

    index = build_faiss_index(
        embeddings
    )

    save_index(
        index,
        EVIDENCE_CORPUS,
    )

    query = (
        "Did unemployment remain around "
        "three percent during 2024?"
    )

    print("\nQUERY")
    print("-" * 70)
    print(query)

    results = search_evidence(
        model=model,
        index=index,
        documents=EVIDENCE_CORPUS,
        query=query,
        top_k=3,
    )

    print("\nTOP EVIDENCE")
    print("-" * 70)

    for result in results:

        print(
            f"\nRank {result['rank']}"
        )

        print(
            f"Evidence: "
            f"{result['evidence_id']}"
        )

        print(
            f"Source: "
            f"{result['source']}"
        )

        print(
            f"Similarity: "
            f"{result['similarity']}"
        )

        print(
            f"Reliability: "
            f"{result['reliability']}"
        )

        print(
            f"Text: "
            f"{result['text']}"
        )

    # ----------------------------------------------------
    # SAVE SEARCH EXAMPLE
    # ----------------------------------------------------

    output_file = (
        ARTIFACT_DIR
        / "local_rag_retrieval_examples.json"
    )

    output = {
        "phase": "8.1",
        "model": MODEL_NAME,
        "query": query,
        "results": results,
    }

    with open(
        output_file,
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
        "PHASE 8.1 LOCAL RETRIEVAL COMPLETE"
    )
    print("=" * 70)

    print(
        f"Saved: {output_file}"
    )

    print("=" * 70)


# ========================================================
# ENTRY POINT
# ========================================================

if __name__ == "__main__":
    run_demo()