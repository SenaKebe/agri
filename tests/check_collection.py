import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.vector_store import VectorStore

store = VectorStore()
info = store.get_collection_info()
print("📦 Collection info:", info)

# Print a few documents from Chroma
collection = store.collection
documents = collection.get(limit=5)
print("\n🧾 Stored Documents:")
for doc, meta in zip(documents["documents"], documents["metadatas"]):
    print(f"- Source: {meta.get('source', 'unknown')}")
    print(f"  Preview: {doc[:200]}...\n")
