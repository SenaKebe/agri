import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.vector_store import VectorStore

# Initialize vector store
store = VectorStore()

query = "When is the best time to plant maize in Ethiopia?"
results = store.search(query=query, n_results=3)

print("\n🔍 Query:", query)
print("Results:")
for r in results:
    print(f"- Rank {r['rank']}: (Score {r['relevance_score']:.3f})")
    print(f"  {r['content'][:200]}...")
    print(f"  Source: {r['metadata'].get('source', 'unknown')}")
    print()
