from pathlib import Path
import chromadb

ROOT_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = ROOT_DIR / "chroma_db"
COLLECTION_NAME = "hotelmind_knowledge"


def get_chroma_collection():
    """
    Load persistent ChromaDB collection.
    Chroma PersistentClient stores vector DB files on disk.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def retrieve_context_chroma(user_question: str, n_results: int = 5) -> str:
    """
    Retrieve semantically relevant knowledge-base chunks from ChromaDB.
    """
    collection = get_chroma_collection()

    try:
        results = collection.query(
            query_texts=[user_question],
            n_results=n_results
        )
    except Exception as e:
        return f"Chroma retrieval error: {e}"

    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not docs:
        return ""

    chunks = []
    for doc, meta in zip(docs, metadatas):
        source = meta.get("source", "unknown")
        chunk_index = meta.get("chunk_index", "NA")
        chunks.append(f"[Source: {source}, chunk: {chunk_index}]\n{doc}")

    return "\n\n".join(chunks)
