### /src/rag
- `manager.py` - Main RAG orchestrator
- `embeddings.py` - Chunking logic, embedding model management, and cosine similarity calculations

## RAG Process

1. **Initialization** (on chat start):
   - Scan `/memory` directory for `.md` and `.txt` files (excluding README)
   - Read files and chunk by characters (~800 chars/chunk = ~200 tokens)
   - Smart chunking respects natural boundaries (paragraphs, lines, sentences, word breaks)
   - Load embedding model (`all-MiniLM-L6-v2` via `sentence-transformers`)
   - Generate embeddings for all chunks (batch processing for speed)
   - Store chunks and embeddings in memory

2. **Query-Time Retrieval** (each user message):
   - Generate embedding for user's query
   - Calculate cosine similarity between query and all chunk embeddings
   - Select top-k most similar chunks (ranked by relevance)
   - Use tokenizer for precise token counting
   - Fit retrieved chunks within RAG token budget (25% of context window)

3. **Prompt Construction** (in `context_manager.py`):
   - System prompt (always included, ~100-500 tokens)
   - RAG context (retrieved chunks, up to 25% of context window)
   - Chat history (fills remaining ~70%, pruned as needed)

4. **Model Generation**:
   - Model receives enriched prompt with relevant knowledge base context
   - Generates informed response using both chat history and RAG context
   - RAG context is ephemeral (not saved to chat history, re-retrieved each query)