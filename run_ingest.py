from app.rag.vector_store import VectorStore

if __name__ == "__main__":
    store = VectorStore()
    success = store.initialize_knowledge_base()

    if success:
        print("✅ Knowledge base initialized successfully!")
        info = store.get_collection_info()
        print(info)
    else:
        print("❌ Failed to initialize knowledge base.")
