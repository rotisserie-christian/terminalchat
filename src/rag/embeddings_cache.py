import os
import pickle
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from ..utils.exceptions import CacheError
from ..utils.atomic_writes import atomic_write_pickle


logger = logging.getLogger(__name__)


class EmbeddingsCache:
    """
    Manages persistent cache of file embeddings
    
    Cache structure:
    {
        "filename.md": {
            "timestamp": 1234567890.0,  # File modification time
            "chunks": ["chunk1", "chunk2", ...],
            "embeddings": [[0.1, 0.2, ...], ...]  # As list for pickle
        }
    }
    
    Note: Embeddings are stored as lists but returned as float32 numpy arrays
    to match the dtype of fresh embeddings from sentence-transformers.
    """
    
    def __init__(self, cache_file: str = ".embeddings_cache.pkl"):
        """
        Initialize embedding cache
        
        Args:
            cache_file: Name of cache file (stored in memory directory)
        """

        self.cache_file = cache_file
        self.cache: Dict = {}
    
    def load(self, memory_dir: str) -> bool:
        """
        Load cache from disk
        
        Args:
            memory_dir: Directory where cache file is stored
            
        Returns:
            True if cache loaded successfully, False otherwise
            
        Raises:
            CacheError: If cache file is corrupted beyond recovery
        """

        cache_path = os.path.join(memory_dir, self.cache_file)
        
        if not os.path.exists(cache_path):
            logger.info("No cache file found, starting fresh")
            self.cache = {}
            return True
        
        try:
            with open(cache_path, 'rb') as f:
                self.cache = pickle.load(f)
            
            # Validate cache structure
            if not isinstance(self.cache, dict):
                logger.warning("Cache has invalid structure, resetting")
                self.cache = {}
                return True
            
            logger.info(f"Loaded cache with {len(self.cache)} entries")
            return True
            
        except pickle.UnpicklingError as e:
            logger.error(f"Cache file is corrupted: {e}")
            raise CacheError(f"Cache file corrupted, delete {cache_path} and retry") from e
        except EOFError as e:
            logger.warning(f"Cache file truncated, resetting: {e}")
            self.cache = {}
            return True
        except Exception as e:
            logger.error(f"Failed to load cache: {e}. Starting fresh.", exc_info=True)
            self.cache = {}
            return False
    
    def save(self, memory_dir: str) -> bool:
        """
        Save cache to disk
    
        Args:
            memory_dir: Directory where cache file should be stored
            
        Returns:
            True if save successful, False otherwise
            
        Raises:
            CacheError: If cache cannot be saved
        """

        cache_path = os.path.join(memory_dir, self.cache_file)
        
        try:
            # Ensure directory exists
            os.makedirs(memory_dir, exist_ok=True)
            
            # Use shared atomic write utility
            atomic_write_pickle(self.cache, cache_path)
            
            logger.info(f"Saved cache with {len(self.cache)} entries")
            return True
            
        except PermissionError as e:
            logger.error(f"Permission denied writing cache: {cache_path}")
            raise CacheError(f"Cannot write cache: Permission denied") from e
        except OSError as e:
            logger.error(f"OS error saving cache: {e}", exc_info=True)
            raise CacheError(f"Failed to save cache: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error saving cache: {e}", exc_info=True)
            return False
    
    def get(self, filename: str, filepath: str) -> Optional[Tuple[List[str], np.ndarray]]:
        """
        Get cached chunks and embeddings for a file if still valid
        
        Checks if:
        1. File exists in cache
        2. Cached timestamp matches current file timestamp
        
        Args:
            filename: Name of the file
            filepath: Full path to the file
            
        Returns:
            Tuple of (chunks, embeddings) if cache valid, None otherwise.
            Embeddings are returned as float32 to match sentence-transformers output.
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
        if cached_entry.get('timestamp') != current_timestamp:
            logger.debug(f"Cache miss: {filename} modified (timestamp changed)")
            return None
        
        # Validate cache entry structure
        if 'chunks' not in cached_entry or 'embeddings' not in cached_entry:
            logger.warning(f"Cache entry for {filename} has invalid structure")
            return None
        
        try:
            # Cache hit!
            chunks = cached_entry['chunks']
            
            # FIXED: Force float32 dtype to match sentence-transformers output
            # This prevents "float != double" errors in cosine similarity calculations
            embeddings = np.array(cached_entry['embeddings'], dtype=np.float32)
            
            logger.debug(f"Cache hit: {filename} ({len(chunks)} chunks)")
            return chunks, embeddings
            
        except Exception as e:
            logger.warning(f"Failed to load cached data for {filename}: {e}")
            return None
    
    def set(self, filename: str, filepath: str, chunks: List[str], embeddings: np.ndarray):
        """
        Store chunks and embeddings in cache
        
        Args:
            filename: Name of the file
            filepath: Full path to the file
            chunks: List of text chunks
            embeddings: Numpy array of embeddings (will be stored as list)
        """

        try:
            timestamp = os.path.getmtime(filepath)
        except OSError as e:
            logger.warning(f"Could not get timestamp for {filename}: {e}")
            return
        
        try:
            self.cache[filename] = {
                'timestamp': timestamp,
                'chunks': chunks,
                'embeddings': embeddings.tolist()  # Convert numpy to list for pickle
            }
            
            logger.debug(f"Cached {filename} ({len(chunks)} chunks)")
            
        except Exception as e:
            logger.error(f"Failed to cache {filename}: {e}", exc_info=True)
    
    def invalidate(self, filename: str):
        """
        Remove a file from cache
        
        Args:
            filename: Name of file to remove from cache
        """

        if filename in self.cache:
            del self.cache[filename]
            logger.debug(f"Invalidated cache for {filename}")
    
    def clean(self, existing_files: List[str]):
        """
        Remove cache entries for files that no longer exist
        
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
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """

        try:
            total_chunks = sum(
                len(entry.get('chunks', [])) 
                for entry in self.cache.values()
            )
            
            return {
                'num_files': len(self.cache),
                'total_chunks': total_chunks,
                'files': list(self.cache.keys())
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {
                'num_files': 0,
                'total_chunks': 0,
                'files': []
            }