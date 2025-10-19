import chromadb
from chromadb.config import Settings
import os
import logging
from app.rag.document_processor import document_processor
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.persistence_dir = "./app/data/chroma_db"
        os.makedirs(self.persistence_dir, exist_ok=True)  # Ensure directory exists
        self.client = chromadb.PersistentClient(path=self.persistence_dir)
        self.collection = self.client.get_or_create_collection(
            name="agricultural_knowledge",
            metadata={"description": "Agricultural knowledge base for crop advisory"}
        )
        self.is_initialized = False
    
    def initialize_knowledge_base(self, documents_dir: str = "./app/data/documents"):
        """Initialize the knowledge base with documents"""
        if self.is_initialized:
            logger.info("Knowledge base already initialized")
            return True
            
        try:
            # Process documents
            documents = document_processor.process_documents(documents_dir)
            
            if not documents:
                logger.warning("No documents found to initialize knowledge base")
                return False
            
            # Add to vector store
            self.collection.add(
                documents=[doc['content'] for doc in documents],
                metadatas=[doc['metadata'] for doc in documents],
                ids=[doc['id'] for doc in documents]
            )
            
            self.is_initialized = True
            logger.info(f"Knowledge base initialized with {len(documents)} document chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            return False
    
    def search(self, query: str, n_results: int = 3, filter_metadata: Dict = None):
        """Search for similar documents with enhanced results"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results nicely
            formatted_results = []
            if results['documents']:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0] if results['distances'] else [1.0] * len(results['documents'][0])
                )):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'relevance_score': 1 - distance,  # Convert distance to similarity score
                        'rank': i + 1
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def get_collection_info(self):
        """Get information about the collection - FIXED VERSION"""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "is_initialized": self.is_initialized
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {
                "document_count": 0,
                "is_initialized": False
            }
    
    def clear_knowledge_base(self):
        """Clear the knowledge base (for testing)"""
        try:
            self.client.delete_collection("agricultural_knowledge")
            self.collection = self.client.get_or_create_collection(
                name="agricultural_knowledge",
                metadata={"description": "Agricultural knowledge base for crop advisory"}
            )
            self.is_initialized = False
            logger.info("Knowledge base cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {str(e)}")
            return False

# Initialize vector store
vector_store = VectorStore()