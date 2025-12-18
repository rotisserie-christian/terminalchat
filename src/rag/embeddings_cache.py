import os
import pickle
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np


logger = logging.getLogger(__name__)


class EmbeddingsCache:
    """
    Manages persistent cache of file embeddings.
    
    Cache structure:
    {
        "filename.md": {
            "timestamp": 1234567890.0,  # File modification time
            "chunks": ["chunk1", "chunk2", ...],
            "embeddings": [[0.1, 0.2, ...], ...]  # As list for pickle
        }
    }
    """
    
    def __init__(self, cache_file: str = ".embeddings_cache.pkl"):
        """
        Initialize embedding cache.
        
        Args:
            cache_file: Name of cache file (stored in memory directory)
        """
        self.cache_file = cache_file
        self.cache: Dict = {}
    
    def load(self, memory_dir: str) -> bool:
        """
        Load cache from disk.
        
        Args:
            memory_dir: Directory where cache file is stored
            
        Returns:
            True if cache loaded successfully, False otherwise
        """
        cache_path = os.path.join(memory_dir, self.cache_file)
        
        if not os.path.exists(cache_path):
            logger.info("No cache file found, starting fresh")
            self.cache = {}
            return True
        
        try:
            with open(cache_path, 'rb') as f:
                self.cache = pickle.load(f)
            logger.info(f"Loaded cache with {len(self.cache)} entries")
            return True
        except Exception as e:
            logger.error(f"Failed to load cache: {e}. Starting fresh.")
            self.cache = {}
            return False
    
    def save(self, memory_dir: str) -> bool:
        """
        Save cache to disk.
        
        Args:
            memory_dir: Directory where cache file should be stored
            
        Returns:
            True if save successful, False otherwise
        """
        cache_path = os.path.join(memory_dir, self.cache_file)
        
        try:
            # Ensure directory exists
            os.makedirs(memory_dir, exist_ok=True)
            
            with open(cache_path, 'wb') as f:
                pickle.dump(self.cache, f)
            logger.info(f"Saved cache with {len(self.cache)} entries")
            return True
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            return False
    
    def get(self, filename: str, filepath: str) -> Optional[Tuple[List[str], np.ndarray]]:
        """
        Get cached chunks and embeddings for a file if still valid.
        
        Checks if:
        1. File exists in cache
        2. Cached timestamp matches current file timestamp
        
        Args:
            filename: Name of the file
            filepath: Full path to the file
            
        Returns:
            Tuple of (chunks, embeddings) if cache valid, None otherwise
        """
        if filename not in self.cache:
            logger.debug(f"Cache miss: {filename} not in cache")
            return None
        
        cached_entry = self.cache[filename]
        
        try:
            current_timestamp = os.path.getmtime(filepath)
        except OSError as e:
            logger.warning(f"Could not get timestamp for {filename}: {e}")
            return None
        
        # Check if file has been modified
        if cached_entry['timestamp'] != current_timestamp:
            logger.debug(f"Cache miss: {filename} modified (timestamp changed)")
            return None
        
        # Cache hit!
        chunks = cached_entry['chunks']
        embeddings = np.array(cached_entry['embeddings'])
        
        logger.debug(f"Cache hit: {filename} ({len(chunks)} chunks)")
        return chunks, embeddings
    
    def set(self, filename: str, filepath: str, chunks: List[str], embeddings: np.ndarray):
        """
        Store chunks and embeddings in cache.
        
        Args:
            filename: Name of the file
            filepath: Full path to the file
            chunks: List of text chunks
            embeddings: Numpy array of embeddings
        """
        try:
            timestamp = os.path.getmtime(filepath)
        except OSError as e:
            logger.warning(f"Could not get timestamp for {filename}: {e}")
            return
        
        self.cache[filename] = {
            'timestamp': timestamp,
            'chunks': chunks,
            'embeddings': embeddings.tolist()  # Convert numpy to list for pickle
        }
        
        logger.debug(f"Cached {filename} ({len(chunks)} chunks)")
    
    def invalidate(self, filename: str):
        """
        Remove a file from cache.
        
        Args:
            filename: Name of file to remove from cache
        """
        if filename in self.cache:
            del self.cache[filename]
            logger.debug(f"Invalidated cache for {filename}")
    
    def clean(self, existing_files: List[str]):
        """
        Remove cache entries for files that no longer exist.
        
        Args:
            existing_files: List of filenames that currently exist
        """
        existing_set = set(existing_files)
        removed = []
        
        for filename in list(self.cache.keys()):
            if filename not in existing_set:
                del self.cache[filename]
                removed.append(filename)
        
        if removed:
            logger.info(f"Cleaned cache: removed {len(removed)} deleted files")
    
    def clear(self):
        """Clear all cache entries."""
        self.cache = {}
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_chunks = sum(len(entry['chunks']) for entry in self.cache.values())
        
        return {
            'num_files': len(self.cache),
            'total_chunks': total_chunks,
            'files': list(self.cache.keys())
        }