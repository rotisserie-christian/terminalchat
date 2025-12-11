# Terminal Chat

A terminal-based chat interface for local language models.
It's meant to be a simple and free system for brainstorming ideas with total privacy.

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/rotisserie-christian/terminalchat
   ```

2. Install dependencies (Python 3.10+):
   ```bash
   pip install -r requirements.txt
   ```

3. Install CLI:
   ```bash
   pip install -e .
   ```

## Usage

Run the main script:

```bash
python main.py
```

Run with CLI:
```bash
terminalchat 
```

### Main Menu
- **New Chat**: Start a fresh conversation.
- **Load Chat**: Browse and resume a previously saved session.
- **Settings**: Configure the model (HuggingFace ID), display names, and interface colors.
- **Exit**: Close the application.

### Controls
- **Arrow Keys**: Navigate menus.
- **Enter**: Select an option or send a message.
- **Exit/Quit**: Type `exit` or `quit` during a chat to save and return to the menu/close.

## Configuration

Settings are stored in `config.json`. You can modify this file directly or use the "Settings" menu option within the application.

## Project Structure

- `main.py`: Application entry point.
- `src/`: Source code modules. See `src/README.md` for details.
- `chats/`: Directory where chat history is saved (JSON format).
- `config.json`: User configuration file.
