from typing import List
from sentence_transformers import SentenceTransformer, util
import numpy as np


def chunk_text(text: str, max_chars: int = 800, overlap_chars: int = 120) -> List[str]:
    """
    Split text into chunks with smart boundary detection.
    
    Respects natural text boundaries in priority order:
    1. Double newline (paragraphs/sections)
    2. Single newline (lines/sentences)
    3. Sentence endings (., !, ?)
    4. Word boundaries (spaces)
    5. Hard break (last resort)
    
    Args:
        text: Input text to chunk
        max_chars: Maximum characters per chunk (~200 tokens at 4 chars/token)
        overlap_chars: Characters to overlap between chunks for context continuity
        
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + max_chars
        
        # Last chunk - take everything remaining
        if end >= text_len:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break
        
        # Find best break point
        break_point = _find_break_point(text, start, end, overlap_chars)
        chunk = text[start:break_point].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start forward, with overlap
        start = break_point - overlap_chars
        if start <= chunks[-1].find(chunk):  # Prevent infinite loop
            start = break_point
    
    return chunks


def _find_break_point(text: str, start: int, end: int, overlap: int) -> int:
    """
    Find the best place to break a chunk based on natural boundaries.
    
    Searches within a window around the target end position for the best
    boundary marker (paragraph break, line break, sentence end, etc.)
    
    Args:
        text: Full text being chunked
        start: Start position of current chunk
        end: Target end position
        overlap: Size of overlap region to search
        
    Returns:
        Position to break the chunk
    """
    # Define search window around target end
    search_start = max(start, end - overlap)
    search_end = min(len(text), end + overlap)
    search_window = text[search_start:search_end]
    
    if not search_window:
        return end
    
    # Priority 1: Paragraph break (double newline)
    if '\n\n' in search_window:
        pos = search_window.rfind('\n\n')
        return search_start + pos + 2
    
    # Priority 2: Line break (single newline)
    if '\n' in search_window:
        pos = search_window.rfind('\n')
        return search_start + pos + 1
    
    # Priority 3: Sentence endings
    for punct in ['. ', '! ', '? ']:
        if punct in search_window:
            pos = search_window.rfind(punct)
            return search_start + pos + 2
    
    # Priority 4: Word boundary (space)
    if ' ' in search_window:
        pos = search_window.rfind(' ')
        return search_start + pos + 1
    
    # Last resort: Hard break at target position
    return end


def cosine_similarity(query_embedding: np.ndarray, chunk_embeddings: np.ndarray) -> np.ndarray:
    """
    Calculate cosine similarity between query and chunk embeddings.
    
    Args:
        query_embedding: Single query embedding vector
        chunk_embeddings: Array of chunk embedding vectors
        
    Returns:
        Array of similarity scores (higher = more similar)
    """
    return util.cos_sim(query_embedding, chunk_embeddings)[0].numpy()


class EmbeddingModel:
    """
    Wrapper for sentence-transformers embedding model.
    
    Handles model loading and batch encoding with consistent interface.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = None
    
    def load(self) -> bool:
        """
        Load the embedding model.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.model = SentenceTransformer(self.model_name)
            return True
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
            return False
    
    def encode(self, texts: List[str], batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for encoding (larger = faster but more memory)
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        return self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector as numpy array
        """
        return self.encode([text])[0]