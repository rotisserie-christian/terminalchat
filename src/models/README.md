### /src/models
- `__init__.py` - Facade exporting `ContextManager` and `load_system_prompt`
- `context.py` - Manages chat history and context window
- `prompt_formatter.py` - Handles prompt formatting and context pruning logic
- `system.py` - Handles loading and managing system prompts
- `handler.py` - Handles model loading, device management, and high-level generation interface
- `streamer.py` - Handles the logic for streaming text generation from the model
