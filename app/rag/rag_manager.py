import logging
import asyncio
from typing import List, Dict, Any
from app.rag.vector_store import vector_store

logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self):
        self.vector_store = vector_store
        self.initialized = False
    
    def initialize_knowledge_base(self) -> bool:
        """Initialize the RAG knowledge base"""
        try:
            self.initialized = self.vector_store.initialize_knowledge_base()
            return self.initialized
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            self.initialized = False
            return False
    
    def get_agricultural_context(self, query: str, max_results: int = 3) -> str:
        """Get relevant agricultural context for a query"""
        try:
            if not self.initialized:
                # Try to initialize if not done
                self.initialize_knowledge_base()
                if not self.initialized:
                    return "Knowledge base not yet initialized. Using general AI knowledge."
            
            # Search for relevant documents
            results = self.vector_store.search(query, n_results=max_results)
            
            if not results:
                return "No specific agricultural knowledge found for this query. Relying on general knowledge."
            
            # Format context from results
            context_parts = []
            for result in results:
                source_info = result['metadata']['source']
                content = result['content']
                relevance = result.get('relevance_score', 0.8)
                
                # Limit content length to avoid huge prompts
                if len(content) > 500:
                    content = content[:500] + "..."
                
                context_parts.append(f"From {source_info} (relevance: {relevance:.2f}): {content}")
            
            context = "\n\n".join(context_parts)
            logger.info(f"Retrieved {len(results)} context chunks for query: {query}")
            return context
            
        except Exception as e:
            logger.error(f"Error getting agricultural context: {str(e)}")
            return "Error retrieving agricultural knowledge. Using general knowledge base."
    
    def get_knowledge_base_status(self) -> Dict[str, Any]:
        """Get status of the knowledge base"""
        try:
            info = self.vector_store.get_collection_info()
            if isinstance(info, dict):
                return {
                    "status": "initialized" if info.get("is_initialized", False) else "not_initialized",
                    "document_chunks": info.get("document_count", 0),
                    "rag_enabled": info.get("is_initialized", False)
                }
            else:
                return {
                    "status": "error",
                    "document_chunks": 0,
                    "rag_enabled": False,
                    "error": "Unexpected response from vector store"
                }
        except Exception as e:
            logger.error(f"Error getting knowledge base status: {str(e)}")
            return {
                "status": "error",
                "document_chunks": 0,
                "rag_enabled": False,
                "error": str(e)
            }

# Initialize RAG manager
rag_manager = RAGManager()