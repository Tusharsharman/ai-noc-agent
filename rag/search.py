from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "noc_runbooks"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

DEFAULT_RESULTS = 3


# ---------------------------------------------------------
# Load embedding model
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("AI NOC RAG - SEMANTIC SEARCH")
print("=" * 60)

print("\nLoading embedding model...")

model = SentenceTransformer(
    EMBEDDING_MODEL
)

print(
    f"Embedding model loaded: {EMBEDDING_MODEL}"
)


# ---------------------------------------------------------
# Initialize ChromaDB
# ---------------------------------------------------------

print("\nConnecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

print(
    f"Collection loaded: {COLLECTION_NAME}"
)

print(
    f"Stored chunks: {collection.count()}"
)


# ---------------------------------------------------------
# Semantic search
# ---------------------------------------------------------

def search_runbooks(
    query: str,
    n_results: int = DEFAULT_RESULTS,
):
    """
    Search the runbook knowledge base using
    semantic similarity.
    """

    if not query.strip():
        return []

    query_embedding = model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(
            n_results,
            collection.count()
        ),
    )

    matches = []

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    for index, document in enumerate(
        documents
    ):
        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        matches.append(
            {
                "document": document,
                "source": metadata.get(
                    "source"
                ),
                "chunk_index": metadata.get(
                    "chunk_index"
                ),
                "distance": distance,
            }
        )

    return matches


# ---------------------------------------------------------
# Display search results
# ---------------------------------------------------------

def print_results(
    query: str,
    results: list,
):
    print("\n")
    print("=" * 60)
    print("RAG SEARCH RESULTS")
    print("=" * 60)

    print(
        f"\nQuery:\n{query}"
    )

    print(
        f"\nResults found: {len(results)}"
    )

    if not results:
        print(
            "\nNo relevant runbook content found."
        )
        return

    for index, result in enumerate(
        results,
        start=1
    ):
        print("\n" + "-" * 60)

        print(
            f"Result {index}"
        )

        print(
            f"Source: "
            f"{result['source']}"
        )

        print(
            f"Chunk: "
            f"{result['chunk_index']}"
        )

        print(
            f"Distance: "
            f"{result['distance']}"
        )

        print(
            "\nContent:"
        )

        print(
            result["document"]
        )

    print("\n" + "=" * 60)


# ---------------------------------------------------------
# Main test
# ---------------------------------------------------------

if __name__ == "__main__":

    queries = [
        (
            "Kubernetes pod is stuck in "
            "ImagePullBackOff and image cannot be pulled"
        ),
        (
            "Application is returning HTTP 500 "
            "errors and error logs are increasing"
        ),
    ]

    for query in queries:

        results = search_runbooks(
            query=query,
            n_results=3,
        )

        print_results(
            query=query,
            results=results,
        )

    print("\n")
    print("=" * 60)
    print("RAG SEMANTIC SEARCH TEST COMPLETED")
    print("=" * 60)
