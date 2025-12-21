# Testing Documentation

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src
```

### Run Specific Test File
```bash
pytest tests/unit/test_model_handler.py
```

### Run Specific Test
```bash
pytest tests/unit/test_model_handler.py::TestModelHandler::test_load_success
```

### View HTML Coverage Report
```bash
start htmlcov/index.html
```

## Test Structure

### Unit Tests (`tests/unit/`)
Tests for individual modules in isolation using mocks for external dependencies.

#### `test_config.py`
**Module Under Test**: `src/config.py`

- Configuration loading and validation
- Default value handling
- JSON parsing error handling
- Configuration updates and persistence

#### `test_context_manager.py`
**Module Under Test**: `src/context_manager.py`

- Message history management
- System prompt integration
- Token-based context window trimming
- Prompt formatting for model input

#### `test_model_handler.py`
**Module Under Test**: `src/model_handler.py`

- Model and tokenizer initialization
- Device selection (CUDA/CPU)
- Model loading with error handling
- Context window detection from multiple sources
- Streaming text generation with proper token handling

**Key Mocks**: `AutoTokenizer`, `AutoModelForCausalLM`, `TextIteratorStreamer`, `Thread`

#### `test_session.py`
**Module Under Test**: `src/app/session.py`

- Session initialization with token budget calculation
- RAG context retrieval and error handling
- Prompt preparation coordination
- Response generation delegation

**Key Mocks**: `ModelHandler`, `RAGManager`, `ContextManager`

#### `test_storage.py`
**Module Under Test**: `src/storage.py`

- Chat persistence (save/load)
- Filename generation and validation
- JSON serialization/deserialization
- Chat listing and sorting

#### `test_system_prompt.py`
**Module Under Test**: `src/system_prompt.py`

- System prompt file loading
- Default prompt fallback
- Empty file handling

## Test Fixtures

### Global Fixtures (`tests/conftest.py`)
- `temp_dir`: Temporary directory for file operations
- `mock_config`: Mocked configuration object