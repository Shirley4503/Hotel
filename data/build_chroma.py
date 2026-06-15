from pathlib import Path
import chromadb

ROOT_DIR = Path(__file__).resolve().parents[1]
KB_DIR = ROOT_DIR / "knowledge_base"
CHROMA_DIR = ROOT_DIR / "chroma_db"

COLLECTION_NAME = "hotelmind_knowledge"


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120):
    """
    Simple character-based chunking for markdown files.
    """
    text = text.strip()
    chunks = []

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def build_chroma():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # Clear old collection content by deleting/recreating the collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = []
    documents = []
    metadatas = []

    for md_file in KB_DIR.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            ids.append(f"{md_file.stem}_{i}")
            documents.append(chunk)
            metadatas.append({
                "source": md_file.name,
                "chunk_index": i
            })

    if not documents:
        print("No knowledge base documents found.")
        return

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Built ChromaDB collection: {COLLECTION_NAME}")
    print(f"Stored {len(documents)} chunks in {CHROMA_DIR}")


if __name__ == "__main__":
    build_chroma()
