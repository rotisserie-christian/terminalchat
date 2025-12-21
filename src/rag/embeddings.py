import logging
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks with smart boundary detection"""
    if not text or not text.strip():
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        
        if end >= text_len:
            chunks.append(text[start:].strip())
            break
        
        # Find good breaking point
        chunk_end = end
        para_break = text.rfind('\n\n', start, end)
        if para_break > start:
            chunk_end = para_break + 2
        elif (newline := text.rfind('\n', start, end)) > start:
            chunk_end = newline + 1
        elif (sentence := max(
            text.rfind('. ', start, end),
            text.rfind('! ', start, end),
            text.rfind('? ', start, end)
        )) > start:
            chunk_end = sentence + 2
        elif (space := text.rfind(' ', start, end)) > start:
            chunk_end = space + 1
        
        chunk = text[start:chunk_end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = chunk_end - overlap
        if start <= (len(text[:chunk_end]) if chunks else 0):
            start = chunk_end
    
    return chunks


def cosine_similarity(query_embedding: np.ndarray, chunk_embeddings: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between query and all chunks"""
    query_norm = query_embedding / np.linalg.norm(query_embedding)
    chunk_norms = np.linalg.norm(chunk_embeddings, axis=1, keepdims=True)
    chunks_normalized = chunk_embeddings / chunk_norms
    similarities = np.dot(chunks_normalized, query_norm)
    return similarities


class EmbeddingModel:
    """Wrapper for sentence-transformers model"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
    
    def load(self) -> bool:
        """Load the embedding model"""
        if self.model is not None:
            return True
        
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            return True
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            return False
    
    def encode(self, texts: List[str], batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings.astype(np.float32)
    
    def encode_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        embedding = self.model.encode([text], convert_to_numpy=True)[0]
        return embedding.astype(np.float32)