import os
import PyPDF2
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import hashlib

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.supported_formats = ['.pdf', '.txt']
    
    def load_pdf_document(self, file_path: str) -> List[str]:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_chunks = []
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_chunks.append(text)
                
                logger.info(f"Loaded {len(text_chunks)} pages from {file_path}")
                return text_chunks
                
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            return []
    
    def load_text_document(self, file_path: str) -> List[str]:
        """Load text from .txt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return [content] if content.strip() else []
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            return []
    
    def chunk_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
                
        return chunks
    
    def process_documents(self, documents_dir: str = "./app/data/documents") -> List[Dict[str, Any]]:
        """Process all documents in the directory"""
        processed_documents = []
        
        if not os.path.exists(documents_dir):
            logger.warning(f"Documents directory {documents_dir} does not exist")
            return processed_documents
        
        for filename in os.listdir(documents_dir):
            file_path = os.path.join(documents_dir, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in self.supported_formats:
                continue
                
            logger.info(f"Processing document: {filename}")
            
            if file_ext == '.pdf':
                pages = self.load_pdf_document(file_path)
                for page_num, page_text in enumerate(pages):
                    chunks = self.chunk_text(page_text)
                    for chunk_num, chunk in enumerate(chunks):
                        doc_id = f"{filename}_page{page_num}_chunk{chunk_num}"
                        processed_documents.append({
                            'id': doc_id,
                            'content': chunk,
                            'metadata': {
                                'source': filename,
                                'page': page_num + 1,
                                'chunk': chunk_num + 1,
                                'type': 'agricultural_knowledge'
                            }
                        })
            
            elif file_ext == '.txt':
                content_chunks = self.load_text_document(file_path)
                for chunk_num, chunk in enumerate(content_chunks):
                    smaller_chunks = self.chunk_text(chunk)
                    for sub_chunk_num, sub_chunk in enumerate(smaller_chunks):
                        doc_id = f"{filename}_chunk{sub_chunk_num}"
                        processed_documents.append({
                            'id': doc_id,
                            'content': sub_chunk,
                            'metadata': {
                                'source': filename,
                                'chunk': sub_chunk_num + 1,
                                'type': 'agricultural_knowledge'
                            }
                        })
        
        logger.info(f"Processed {len(processed_documents)} document chunks")
        return processed_documents

# Initialize document processor
document_processor = DocumentProcessor()