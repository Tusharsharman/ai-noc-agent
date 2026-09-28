from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RUNBOOKS_DIR = BASE_DIR / "runbooks"

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "noc_runbooks"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


# ---------------------------------------------------------
# Load embedding model
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("AI NOC RAG - RUNBOOK INGESTION")
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

print("\nInitializing ChromaDB...")

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "description": (
            "AI NOC Agent runbook knowledge base"
        )
    }
)

print(
    f"Collection ready: {COLLECTION_NAME}"
)


# ---------------------------------------------------------
# Chunking
# ---------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
):
    """
    Split text into overlapping character chunks.
    """

    if not text.strip():
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


# ---------------------------------------------------------
# Read runbooks
# ---------------------------------------------------------

def load_runbooks():

    if not RUNBOOKS_DIR.exists():
        raise RuntimeError(
            f"Runbooks directory not found: "
            f"{RUNBOOKS_DIR}"
        )

    files = sorted(
        RUNBOOKS_DIR.glob("*.md")
    )

    if not files:
        raise RuntimeError(
            "No Markdown runbooks found."
        )

    documents = []

    for file_path in files:

        print(
            f"\nReading runbook: "
            f"{file_path.name}"
        )

        text = file_path.read_text(
            encoding="utf-8"
        )

        chunks = chunk_text(text)

        print(
            f"Created {len(chunks)} chunks"
        )

        for index, chunk in enumerate(
            chunks
        ):

            documents.append(
                {
                    "id": (
                        f"{file_path.stem}"
                        f"-chunk-{index}"
                    ),
                    "text": chunk,
                    "source": file_path.name,
                    "chunk_index": index,
                }
            )

    return documents


# ---------------------------------------------------------
# Ingest documents
# ---------------------------------------------------------

def ingest():

    documents = load_runbooks()

    if not documents:
        print(
            "\nNo documents available "
            "for ingestion."
        )
        return

    print(
        f"\nTotal chunks: "
        f"{len(documents)}"
    )

    texts = [
        document["text"]
        for document in documents
    ]

    ids = [
        document["id"]
        for document in documents
    ]

    metadatas = [
        {
            "source": document["source"],
            "chunk_index": document[
                "chunk_index"
            ],
        }
        for document in documents
    ]

    print(
        "\nGenerating embeddings..."
    )

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )

    print(
        "\nStoring documents in ChromaDB..."
    )

    # Remove existing records so that
    # repeated ingestion does not create
    # stale duplicate content.
    try:
        collection.delete(
            where={}
        )
    except Exception:
        pass

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "RAG INGESTION COMPLETED"
    )

    print(
        "=" * 60
    )

    print(
        f"Runbooks directory: "
        f"{RUNBOOKS_DIR}"
    )

    print(
        f"ChromaDB directory: "
        f"{CHROMA_DIR}"
    )

    print(
        f"Collection: "
        f"{COLLECTION_NAME}"
    )

    print(
        f"Documents/chunks stored: "
        f"{len(documents)}"
    )

    print(
        "=" * 60
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":
    ingest()
