import os
import logging
from typing import List, Dict, Tuple, Optional
import numpy as np
from pathlib import Path
from .embeddings import chunk_text, cosine_similarity, EmbeddingModel
from .embeddings_cache import EmbeddingsCache


logger = logging.getLogger(__name__)


MEMORY_DIR = "memory"
SUPPORTED_EXTENSIONS = {'.md', '.txt'}
EXCLUDED_FILES = {'README.md', 'readme.md', 'README.txt', 'readme.txt'}


class RAGManager:
    """
    Manages RAG (Retrieval Augmented Generation) pipeline.
    
    Loads files from /memory directory, chunks them, generates embeddings,
    and retrieves relevant chunks based on query similarity.
    """
    
    def __init__(self, memory_dir: str = MEMORY_DIR, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG manager.
        
        Args:
            memory_dir: Directory containing context files
            embedding_model: Name of sentence-transformers model to use
        """
        self.memory_dir = memory_dir
        self.embedding_model = EmbeddingModel(embedding_model)
        self.cache = EmbeddingsCache()
        
        # Storage for chunks and embeddings
        self.chunks: List[str] = []
        self.embeddings: Optional[np.ndarray] = None
        self.chunk_metadata: List[Dict] = []  # Track source file for each chunk
        
        self._loaded = False
    
    def load(self, show_progress: bool = True) -> bool:
        """
        Load and process all files from memory directory.
        
        Steps:
        1. Load embedding model
        2. Load cache from disk
        3. Read files from memory directory
        4. For each file:
           - Check if cached and unchanged → use cache
           - Otherwise → chunk, embed, and cache
        5. Save updated cache to disk
        
        Args:
            show_progress: Whether to show progress during embedding generation
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Loading RAG context from {self.memory_dir}")
        
        # Load embedding model
        if not self.embedding_model.load():
            logger.error("Failed to load embedding model")
            return False
        
        # Ensure memory directory exists
        if not os.path.exists(self.memory_dir):
            logger.warning(f"Memory directory {self.memory_dir} does not exist. Creating it.")
            os.makedirs(self.memory_dir)
            return True  # No files to load, but not an error
        
        # Load cache
        self.cache.load(self.memory_dir)
        
        # Track files to process and files that need embedding
        all_chunks = []
        all_embeddings_list = []
        all_metadata = []
        files_to_embed = []
        chunks_to_embed = []
        
        existing_files = []
        
        for filename in os.listdir(self.memory_dir):
            filepath = os.path.join(self.memory_dir, filename)
            
            # Skip directories and unsupported files
            if not os.path.isfile(filepath):
                continue
            
            # Skip excluded files (README, etc.)
            if filename in EXCLUDED_FILES:
                logger.debug(f"Skipping excluded file: {filename}")
                continue
            
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                logger.debug(f"Skipping unsupported file: {filename}")
                continue
            
            existing_files.append(filename)
            
            # Try to get from cache first
            cached_result = self.cache.get(filename, filepath)
            
            if cached_result is not None:
                # Cache hit - use cached data
                file_chunks, file_embeddings = cached_result
                all_chunks.extend(file_chunks)
                all_embeddings_list.append(file_embeddings)
                
                # Track metadata for each chunk
                for chunk in file_chunks:
                    all_metadata.append({
                        'filename': filename,
                        'filepath': filepath
                    })
                
                logger.info(f"Loaded {len(file_chunks)} chunks from {filename} (cached)")
                
            else:
                # Cache miss - need to process file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    file_chunks = chunk_text(text)
                    
                    if not file_chunks:
                        logger.warning(f"No chunks generated from {filename}")
                        continue
                    
                    # Store for batch embedding
                    start_idx = len(all_chunks)
                    all_chunks.extend(file_chunks)
                    chunks_to_embed.extend(file_chunks)
                    files_to_embed.append((filename, filepath, start_idx, len(file_chunks)))
                    
                    # Track metadata for each chunk
                    for chunk in file_chunks:
                        all_metadata.append({
                            'filename': filename,
                            'filepath': filepath
                        })
                    
                    logger.info(f"Processing {len(file_chunks)} chunks from {filename}")
                    
                except Exception as e:
                    logger.error(f"Error loading file {filename}: {e}")
                    continue
        
        if not all_chunks and not chunks_to_embed:
            logger.warning(f"No content found in {self.memory_dir}")
            # Clean up cache for deleted files
            self.cache.clean(existing_files)
            self.cache.save(self.memory_dir)
            return True  # Not an error, just no files
        
        # Generate embeddings for new/changed files (batch processing)
        if chunks_to_embed:
            try:
                logger.info(f"Generating embeddings for {len(chunks_to_embed)} new/changed chunks...")
                new_embeddings = self.embedding_model.encode(
                    chunks_to_embed,
                    batch_size=32,
                    show_progress=show_progress
                )
                
                # Update cache for newly processed files
                embed_offset = 0
                for filename, filepath, start_idx, num_chunks in files_to_embed:
                    file_embeddings = new_embeddings[embed_offset:embed_offset + num_chunks]
                    file_chunks = all_chunks[start_idx:start_idx + num_chunks]
                    
                    self.cache.set(filename, filepath, file_chunks, file_embeddings)
                    all_embeddings_list.append(file_embeddings)
                    
                    embed_offset += num_chunks
                
            except Exception as e:
                logger.error(f"Error generating embeddings: {e}")
                return False
        
        # Combine all embeddings
        if all_embeddings_list:
            self.embeddings = np.vstack(all_embeddings_list)
            self.chunks = all_chunks
            self.chunk_metadata = all_metadata
            self._loaded = True
            
            logger.info(f"RAG context loaded: {len(self.chunks)} chunks from {len(set(m['filename'] for m in all_metadata))} files")
        else:
            logger.warning("No embeddings generated")
            return True
        
        # Clean up cache for deleted files and save
        self.cache.clean(existing_files)
        self.cache.save(self.memory_dir)
        
        return True
    
    def retrieve(self, query: str, tokenizer, max_tokens: int, top_k: int = 10) -> Tuple[str, int]:
        """
        Retrieve relevant chunks for a query.
        
        Process:
        1. Generate embedding for query
        2. Calculate cosine similarity with all chunks
        3. Select top-k most similar chunks
        4. Fit chunks within token budget using tokenizer
        
        Args:
            query: User's query text
            tokenizer: Tokenizer for precise token counting
            max_tokens: Maximum tokens allowed for RAG context
            top_k: Number of top similar chunks to consider
            
        Returns:
            Tuple of (concatenated_chunks, total_tokens_used)
        """
        if not self._loaded or not self.chunks:
            logger.debug("No RAG context loaded, returning empty")
            return "", 0
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode_single(query)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)
            
            # Get top-k indices (sorted by similarity, descending)
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Select chunks that fit within token budget
            selected_chunks = []
            total_tokens = 0
            
            for idx in top_indices:
                chunk = self.chunks[idx]
                
                # Calculate tokens for this chunk
                chunk_tokens = len(tokenizer.encode(chunk))
                
                # Check if adding this chunk would exceed budget
                if total_tokens + chunk_tokens > max_tokens:
                    # Try to fit partial chunk if we have room
                    if total_tokens < max_tokens * 0.8:  # Only if we haven't used most of budget
                        continue
                    break
                
                selected_chunks.append(chunk)
                total_tokens += chunk_tokens
                
                logger.debug(f"Retrieved chunk from {self.chunk_metadata[idx]['filename']} "
                           f"(similarity: {similarities[idx]:.3f}, tokens: {chunk_tokens})")
            
            # Concatenate selected chunks
            context = "\n\n".join(selected_chunks)
            
            logger.info(f"Retrieved {len(selected_chunks)} chunks ({total_tokens} tokens) for query")
            return context, total_tokens
            
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return "", 0
    
    def is_loaded(self) -> bool:
        """Check if RAG context has been loaded."""
        return self._loaded
    
    def get_stats(self) -> Dict:
        """
        Get statistics about loaded RAG context.
        
        Returns:
            Dictionary with stats (num_chunks, num_files, etc.)
        """
        if not self._loaded:
            return {
                'loaded': False,
                'num_chunks': 0,
                'num_files': 0
            }
        
        unique_files = set(m['filename'] for m in self.chunk_metadata)
        
        return {
            'loaded': True,
            'num_chunks': len(self.chunks),
            'num_files': len(unique_files),
            'files': sorted(unique_files)
        }