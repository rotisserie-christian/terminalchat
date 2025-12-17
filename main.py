import asyncio
import sys
from src.model_handler import ModelHandler
from src.context_manager import ContextManager
from src.storage import ChatStorage
from src.ui import TerminalUI
from src.settings import ManageSettings
from src.system_prompt import load_system_prompt
from src.rag import RAGManager
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
                setup = ManageSettings(ui.console)
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

        # Initialize RAG Manager if enabled
        rag_manager = None
        if config.RAG_ENABLED:
            ui.display_system_message("Initializing RAG system...")
            rag_manager = RAGManager()
            
            with ui.console.status("[bold green]Loading knowledge base...") as status:
                if rag_manager.load(show_progress=False):
                    stats = rag_manager.get_stats()
                    if stats['num_chunks'] > 0:
                        ui.display_system_message(
                            f"✓ RAG enabled: {stats['num_chunks']} chunks from {stats['num_files']} files"
                        )
                        if stats['files']:
                            ui.display_system_message(f"  Files: {', '.join(stats['files'])}")
                    else:
                        ui.display_system_message("⚠ No files found in /memory directory. RAG disabled.")
                        rag_manager = None
                else:
                    ui.display_error("Failed to load RAG system. Continuing without RAG.")
                    rag_manager = None
        else:
            ui.display_system_message("RAG disabled (enable in Settings)")


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

        # Calculate RAG token budget (configurable percentage of available context)
        available_context = model_handler.context_window - 512  # Reserve 512 for generation
        rag_token_budget = int(available_context * config.RAG_CONTEXT_PERCENTAGE)
        
        # Chat loop
        return_to_menu = False
        while True:
            user_input = ui.get_input()
            
            # Check for manual save signal
            if user_input == 'MANUAL_SAVE':
                saved_file = storage.save_chat(context_manager.get_messages(), loaded_filename)
                ui.display_system_message(f"Chat manually saved to {saved_file}")
                # Update loaded_filename if this was a new chat
                if loaded_filename is None:
                    loaded_filename = saved_file
                continue
            
            # Check for special return to menu signal
            if user_input == 'RETURN_TO_MENU':
                ui.display_system_message("Returning to main menu...")
                return_to_menu = True
                break
            
            if user_input is None:
                # Exit on Ctrl+C at prompt (no auto-save)
                return  # Exit application
            
            if not user_input.strip():
                continue

            context_manager.add_message("user", user_input)
            
            # Retrieve relevant RAG context for this query (if RAG enabled)
            rag_context = ""
            if rag_manager and rag_manager.is_loaded():
                try:
                    rag_context, rag_tokens = rag_manager.retrieve(
                        query=user_input,
                        tokenizer=model_handler.tokenizer,
                        max_tokens=rag_token_budget,
                        top_k=config.RAG_TOP_K
                    )
                    if rag_tokens > 0:
                        ui.display_system_message(f"[dim]Retrieved {rag_tokens} tokens of context[/dim]")
                except Exception as e:
                    ui.display_error(f"RAG retrieval failed: {e}")
                    rag_context = ""
            
            # Prepare prompt with RAG context
            prompt = context_manager.prepare_prompt(
                model_handler.tokenizer, 
                available_context,
                rag_context=rag_context
            )
            
            # Generate and stream response
            try:
                generator = model_handler.generate_stream(prompt)
                full_response = ui.display_model_stream(generator)
                context_manager.add_message("assistant", full_response)
                
                # Autosave after assistant response if enabled
                if config.AUTOSAVE_ENABLED:
                    saved_file = storage.save_chat(context_manager.get_messages(), loaded_filename)
                    # Update loaded_filename if this was a new chat
                    if loaded_filename is None:
                        loaded_filename = saved_file
                    ui.display_system_message(f"[dim]Chat auto-saved to {saved_file}[/dim]")
                
            except KeyboardInterrupt:
                # Handle Ctrl+C during generation (no auto-save)
                ui.display_system_message("\nGeneration interrupted by user.")
                return  # Exit application
            except Exception as e:
                ui.display_error(f"Generation failed: {e}")
        
        # If user wants to return to menu, continue outer loop
        if return_to_menu:
            continue
        else:
            break  # Otherwise exit

if __name__ == "__main__":
    main()