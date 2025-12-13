import asyncio
import sys
from src.model_handler import ModelHandler
from src.context_manager import ContextManager
from src.storage import ChatStorage
from src.ui import TerminalUI
from src.setup_sequence import SetupSequence
from src.system_prompt import (
    load_system_prompt,
    get_default_prompt,
    list_prompts,
    load_prompt,
    set_active_prompt,
    get_active_prompt_path,
)
import src.config as config
import questionary




def main():
    ui = TerminalUI()

    # Load config (defaults or file)
    config.load_config()
    
    storage = ChatStorage()

    # Outer loop: allows returning to menu from chat
    while True:
        loaded_filename = None

        # Main Menu Loop
        while True:
            choice = ui.show_main_menu()
            
            if choice == "Exit":
                sys.exit(0)
            elif choice == "Settings":
                setup = SetupSequence(ui.console)
                setup.run()
                # Reload config after setup
                config.load_config()
                continue

            elif choice == "Load Chat":
                chats = storage.list_chats()
                selected = ui.show_chat_selection(chats)
                if selected:
                    loaded_filename = selected
                    break
            elif choice == "New Chat":
                loaded_filename = None
                break

        # Use model from config
        model_name = config.MODEL_NAME
        
        ui.display_system_message(f"Initializing ModelHandler with {model_name}...")
        model_handler = ModelHandler(model_name)
        
        with ui.console.status("[bold green]Loading model (this may take a while)...") as status:
            if not model_handler.load():
                ui.display_error("Failed to load model. Exiting.")
                return

        context_manager = ContextManager()
        
        # Restore chat if loaded
        if loaded_filename:
            messages = storage.load_chat(loaded_filename)
            if messages:
                context_manager.messages = messages
                ui.display_system_message(f"Chat history loaded from {loaded_filename}")
                # Replay history to screen
                for msg in messages:
                    if msg['role'] == 'user':
                        ui.console.print(f"\n[{config.USER_DISPLAY_NAME}] > {msg['content']}")
                    elif msg['role'] == 'assistant':
                        ui.console.print(f"\n[bold {config.SECONDARY_COLOR}]{config.MODEL_DISPLAY_NAME} >[/bold {config.SECONDARY_COLOR}] {msg['content']}")

        # Chat loop
        return_to_menu = False
        while True:
            user_input = ui.get_input()
            
            # Check for special return to menu signal
            if user_input == 'RETURN_TO_MENU':
                saved_file = storage.save_chat(context_manager.get_messages(), loaded_filename)
                ui.display_system_message(f"Chat saved to {saved_file}")
                ui.display_system_message("Returning to main menu...")
                return_to_menu = True
                break
            
            if user_input is None:
                # Auto-save on exit (Ctrl+C at prompt)
                saved_file = storage.save_chat(context_manager.get_messages(), loaded_filename)
                ui.display_system_message(f"Chat saved to {saved_file}")
                return  # Exit application
            
            if not user_input.strip():
                continue

            context_manager.add_message("user", user_input)
            
            # Prepare prompt
            prompt = context_manager.prepare_prompt(
                model_handler.tokenizer, 
                model_handler.context_window - 512 # Leave room for generation
            )
            
            # Generate and stream response
            try:
                generator = model_handler.generate_stream(prompt)
                full_response = ui.display_assistant_stream(generator)
                context_manager.add_message("assistant", full_response)
            except KeyboardInterrupt:
                # Handle Ctrl+C during generation
                ui.display_system_message("\nGeneration interrupted by user.")
                saved_file = storage.save_chat(context_manager.get_messages(), loaded_filename)
                ui.display_system_message(f"Chat saved to {saved_file}")
                return  # Exit application
            except Exception as e:
                ui.display_error(f"Generation failed: {e}")
        
        # If we broke out of chat loop to return to menu, continue outer loop
        if return_to_menu:
            continue
        else:
            break  # Otherwise exit

if __name__ == "__main__":
    main()
