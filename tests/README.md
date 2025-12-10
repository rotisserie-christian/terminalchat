# Tests

## Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# View HTML coverage report
start htmlcov/index.html
```

## Structure

- `tests/unit/` - Unit tests for core modules
  - `test_storage.py` - ChatStorage save/load/list functionality
  - `test_context_manager.py` - Message management and prompt preparation
  - `test_config.py` - Configuration loading and saving

