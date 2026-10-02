from pathlib import Path
import json
import re
from datetime import datetime, timezone

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# VERILENS
# PHASE 7.3 v2 — IMPROVED EVIDENCE RETRIEVAL
# ============================================================

OUTPUT_DIR = Path("ml/evidence/artifacts")

OUTPUT_PATH = (
    OUTPUT_DIR / "evidence_retrieval_examples.json"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text for retrieval.
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
    Extract normalized word tokens.
    """

    return set(
        normalize_text(text).split()
    )


# ============================================================
# IMPORTANT PHRASES
# ============================================================

def extract_key_phrases(text):
    """
    Extract domain-important phrases.

    Phase 7.3 uses lightweight phrase detection.
    Later phases can replace this with NLP models.
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
# NUMERIC REFERENCES
# ============================================================

def extract_numeric_references(text):
    """
    Extract percentages, years, currencies,
    and other important numeric references.
    """

    patterns = [
        r"\b\d+(?:\.\d+)?%",
        r"\b(?:19|20)\d{2}\b",
        r"\b\d+(?:\.\d+)?\s*(?:million|billion|trillion|thousand)\b",
        r"\$\s*\d+(?:\.\d+)?",
        r"\b\d+(?:\.\d+)?\b",
    ]

    values = []

    normalized = normalize_text(text)

    for pattern in patterns:

        matches = re.findall(
            pattern,
            normalized,
        )

        values.extend(matches)

    return set(values)


# ============================================================
# TOKEN OVERLAP
# ============================================================

def calculate_token_overlap(
    query,
    document,
):
    """
    Calculate token overlap between
    claim and evidence.
    """

    query_tokens = extract_tokens(
        query
    )

    document_tokens = extract_tokens(
        document
    )

    if not query_tokens:
        return 0.0

    overlap = (
        query_tokens
        & document_tokens
    )

    return round(
        len(overlap)
        / len(query_tokens),
        4,
    )


# ============================================================
# KEY PHRASE MATCH
# ============================================================

def calculate_phrase_match(
    query,
    document,
):
    """
    Measure overlap of important domain phrases.
    """

    query_phrases = (
        extract_key_phrases(query)
    )

    document_phrases = (
        extract_key_phrases(document)
    )

    if not query_phrases:
        return 0.0

    overlap = (
        query_phrases
        & document_phrases
    )

    return round(
        len(overlap)
        / len(query_phrases),
        4,
    )


# ============================================================
# NUMERIC MATCH
# ============================================================

def calculate_numeric_match(
    query,
    document,
):
    """
    Measure overlap of important numeric references.
    """

    query_numbers = (
        extract_numeric_references(
            query
        )
    )

    document_numbers = (
        extract_numeric_references(
            document
        )
    )

    if not query_numbers:
        return 0.0

    overlap = (
        query_numbers
        & document_numbers
    )

    return round(
        len(overlap)
        / len(query_numbers),
        4,
    )


# ============================================================
# TOPIC MATCH
# ============================================================

def calculate_topic_match(
    query,
    document,
):
    """
    Lightweight topic matching.

    Important subject phrases receive
    stronger importance than generic words.
    """

    query_phrases = (
        extract_key_phrases(query)
    )

    document_phrases = (
        extract_key_phrases(document)
    )

    if not query_phrases:
        return 0.0

    overlap = (
        query_phrases
        & document_phrases
    )

    return round(
        len(overlap)
        / len(query_phrases),
        4,
    )


# ============================================================
# RETRIEVAL SCORE
# ============================================================

def calculate_retrieval_score(
    semantic_similarity,
    token_overlap,
    phrase_match,
    numeric_match,
    topic_match,
):
    """
    Calculate transparent evidence retrieval score.

    We intentionally prioritize:
    1. semantic similarity
    2. domain phrase match
    3. numeric reference match
    4. token overlap

    Topic match reinforces important subject alignment.
    """

    score = (

        0.40
        * semantic_similarity

        + 0.15
        * token_overlap

        + 0.20
        * phrase_match

        + 0.15
        * numeric_match

        + 0.10
        * topic_match
    )

    return round(
        score,
        4,
    )


# ============================================================
# EVIDENCE RETRIEVAL
# ============================================================

def retrieve_evidence(
    claim,
    evidence_corpus,
    top_k=3,
):
    """
    Retrieve and rank evidence candidates.
    """

    if not evidence_corpus:
        return []

    documents = [
        item["text"]
        for item in evidence_corpus
    ]

    normalized_claim = normalize_text(
        claim
    )

    normalized_documents = [
        normalize_text(document)
        for document in documents
    ]

    # ========================================================
    # TF-IDF
    # ========================================================

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )

    matrix = vectorizer.fit_transform(
        [
            normalized_claim,
            *normalized_documents,
        ]
    )

    claim_vector = matrix[0]

    document_vectors = matrix[1:]

    similarities = cosine_similarity(
        claim_vector,
        document_vectors,
    )[0]

    # ========================================================
    # SCORE EACH DOCUMENT
    # ========================================================

    results = []

    for index, document in enumerate(
        evidence_corpus
    ):

        document_text = document["text"]

        semantic_similarity = float(
            similarities[index]
        )

        token_overlap = (
            calculate_token_overlap(
                claim,
                document_text,
            )
        )

        phrase_match = (
            calculate_phrase_match(
                claim,
                document_text,
            )
        )

        numeric_match = (
            calculate_numeric_match(
                claim,
                document_text,
            )
        )

        topic_match = (
            calculate_topic_match(
                claim,
                document_text,
            )
        )

        retrieval_score = (
            calculate_retrieval_score(
                semantic_similarity,
                token_overlap,
                phrase_match,
                numeric_match,
                topic_match,
            )
        )

        result = {

            "evidence_id": document[
                "evidence_id"
            ],

            "source_id": document[
                "source_id"
            ],

            "title": document[
                "title"
            ],

            "publisher": document[
                "publisher"
            ],

            "url": document[
                "url"
            ],

            "excerpt": document[
                "text"
            ],

            "semantic_similarity": round(
                semantic_similarity,
                4,
            ),

            "token_overlap": (
                token_overlap
            ),

            "phrase_match": (
                phrase_match
            ),

            "numeric_match": (
                numeric_match
            ),

            "topic_match": (
                topic_match
            ),

            "retrieval_score": (
                retrieval_score
            ),

            "retrieval_rank": None,
        }

        results.append(result)

    # ========================================================
    # RANK
    # ========================================================

    results.sort(
        key=lambda item: item[
            "retrieval_score"
        ],
        reverse=True,
    )

    results = results[:top_k]

    for rank, result in enumerate(
        results,
        start=1,
    ):

        result[
            "retrieval_rank"
        ] = rank

    return results


# ============================================================
# LOCAL EVIDENCE CORPUS
# ============================================================

def build_demo_corpus():

    """
    Synthetic local corpus.

    These documents exist only to test
    retrieval architecture.

    They are NOT real-world evidence.
    """

    return [

        {
            "evidence_id": "evidence_0001",

            "source_id": "source_0001",

            "title": (
                "Employment Statistics Report"
            ),

            "publisher": (
                "Example Statistics Bureau"
            ),

            "url": (
                "https://example.org/"
                "employment-statistics"
            ),

            "text": (
                "The unemployment rate "
                "declined to approximately "
                "3 percent during 2024."
            ),
        },

        {
            "evidence_id": "evidence_0002",

            "source_id": "source_0002",

            "title": (
                "Annual Labor Market Review"
            ),

            "publisher": (
                "Example Research Institute"
            ),

            "url": (
                "https://example.org/"
                "labor-market-review"
            ),

            "text": (
                "The unemployment rate "
                "remained near 3.2 percent "
                "throughout much of 2024."
            ),
        },

        {
            "evidence_id": "evidence_0003",

            "source_id": "source_0003",

            "title": (
                "Employment Analysis"
            ),

            "publisher": (
                "Example News Organization"
            ),

            "url": (
                "https://example.org/"
                "employment-analysis"
            ),

            "text": (
                "Some estimates placed the "
                "annual unemployment rate "
                "closer to 4 percent."
            ),
        },

        {
            "evidence_id": "evidence_0004",

            "source_id": "source_0004",

            "title": (
                "Inflation Report 2024"
            ),

            "publisher": (
                "Example Economic Institute"
            ),

            "url": (
                "https://example.org/"
                "inflation-report"
            ),

            "text": (
                "Consumer price inflation "
                "showed a gradual decline "
                "during the second half "
                "of 2024."
            ),
        },

        {
            "evidence_id": "evidence_0005",

            "source_id": "source_0005",

            "title": (
                "Population Statistics"
            ),

            "publisher": (
                "Example Statistics Office"
            ),

            "url": (
                "https://example.org/"
                "population-statistics"
            ),

            "text": (
                "The national population "
                "increased during 2024 "
                "according to annual estimates."
            ),
        },
    ]


# ============================================================
# DEMO CLAIMS
# ============================================================

def build_demo_claims():

    return [

        (
            "The unemployment rate "
            "dropped to 3% in 2024."
        ),

        (
            "Inflation declined during "
            "the second half of 2024."
        ),

        (
            "The national population "
            "increased in 2024."
        ),
    ]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "VERILENS - PHASE 7.3 v2"
    )

    print(
        "IMPROVED EVIDENCE RETRIEVAL"
    )

    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    evidence_corpus = (
        build_demo_corpus()
    )

    claims = build_demo_claims()

    all_results = []

    # ========================================================
    # PROCESS CLAIMS
    # ========================================================

    for claim in claims:

        print(
            "\n" + "-" * 70
        )

        print(
            f"CLAIM: {claim}"
        )

        retrieved = retrieve_evidence(
            claim=claim,
            evidence_corpus=evidence_corpus,
            top_k=3,
        )

        print(
            "\nTOP EVIDENCE"
        )

        for result in retrieved:

            print(
                f"\nRank "
                f"{result['retrieval_rank']}"
            )

            print(
                f"  Evidence: "
                f"{result['evidence_id']}"
            )

            print(
                f"  Source: "
                f"{result['title']}"
            )

            print(
                f"  Semantic similarity: "
                f"{result['semantic_similarity']}"
            )

            print(
                f"  Token overlap: "
                f"{result['token_overlap']}"
            )

            print(
                f"  Phrase match: "
                f"{result['phrase_match']}"
            )

            print(
                f"  Numeric match: "
                f"{result['numeric_match']}"
            )

            print(
                f"  Topic match: "
                f"{result['topic_match']}"
            )

            print(
                f"  Retrieval score: "
                f"{result['retrieval_score']}"
            )

            print(
                f"  Excerpt: "
                f"{result['excerpt']}"
            )

        all_results.append(
            {
                "claim": claim,
                "retrieved_evidence": retrieved,
            }
        )

    # ========================================================
    # OUTPUT
    # ========================================================

    output = {

        "schema_version": "2.0",

        "generated_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),

        "retrieval_method": {

            "semantic_method": (
                "TF-IDF cosine similarity"
            ),

            "token_overlap": True,

            "key_phrase_matching": True,

            "numeric_reference_matching": True,

            "topic_matching": True,

            "score_formula": (
                "0.40 * semantic_similarity "
                "+ 0.15 * token_overlap "
                "+ 0.20 * phrase_match "
                "+ 0.15 * numeric_match "
                "+ 0.10 * topic_match"
            ),

            "top_k": 3,
        },

        "corpus_size": len(
            evidence_corpus
        ),

        "claims_processed": len(
            claims
        ),

        "results": all_results,
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
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "IMPROVED EVIDENCE RETRIEVAL COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Corpus documents: "
        f"{len(evidence_corpus)}"
    )

    print(
        f"Claims processed: "
        f"{len(claims)}"
    )

    print(
        "Retrieval signals:"
    )

    print(
        "  - TF-IDF semantic similarity"
    )

    print(
        "  - Token overlap"
    )

    print(
        "  - Key phrase matching"
    )

    print(
        "  - Numeric reference matching"
    )

    print(
        "  - Topic matching"
    )

    print(
        f"\nSaved: {OUTPUT_PATH}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()