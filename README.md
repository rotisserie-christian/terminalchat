# Terminal Chat

A terminal-based chat interface for local language models. It has rag and saving features, disabled by default but easily customizable. It's meant to be a simple harness for getting started with whatever you want to make.  

## Installation

Clone the repo:
```bash
git clone https://github.com/rotisserie-christian/terminalchat
```


Install dependencies (Python 3.10+):
```bash
pip install -r requirements.txt
```


Install CLI:
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
- **Exit/Quit**: `ctrl + c` or `exit` in the main menu.

## Configuration

Settings are stored in `config.json`. You can modify this file directly or use the "Settings" menu option within the application.

## Project Structure

- `main.py`: Entry point.
- `src/`: See `src/README.md`
- `chats/`: Where chat history is saved (JSON format).
- `prompts/`: System prompts.
- `tests/`: See `tests/README.md`
- `config.json`: 👍
