import os
from dotenv import load_dotenv
from providers import AnthropicProvider, MockProvider
from chatbot import ChatBot
from database import ChatDatabase

# Load API key from .env file into environment variables
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")


# Safety check — fail loudly if no API key is set
if not API_KEY:
    raise ValueError("No ANTHROPIC_API_KEY found in .env file!")


def main():
    # Create the provider (this is what talks to Claude)
    provider = AnthropicProvider(api_key=API_KEY)
    db = ChatDatabase()



    
    # Create the bot with a system prompt of your choice
    # Change this string to give your bot a different personality!
    bot = ChatBot(
        database=db,
        provider=provider,
        system_prompt="You are a friendly Python tutor who explains things simply with examples.",
        title="Testing the product"
    )
    
    # Welcome message
    print("=" * 50)
    print("🤖 Chatbot ready!")
    print("Commands:")
    print("  - Type your message to chat")
    print("  - 'history' → show conversation so far")
    print("  - 'reset'   → clear the conversation")
    print("  - 'quit'    → exit the chatbot")
    print("=" * 50)
    print()
    
    # The REPL loop (Read-Eval-Print-Loop)
    while True:
        # 1. READ — get user input
        user_input = input("You: ").strip()
        
        # Skip empty messages
        if not user_input:
            continue
        
        # Handle special commands
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye! 👋")
            db.close()
            break
        
        if user_input.lower() == "history":
            bot.show_history()
            print()
            continue
        
        if user_input.lower() == "reset":
            bot.reset()
            print("Conversation cleared. ✨\n")
            continue

        # Handle 'list' command
        if user_input.lower() == "list":
            conversations = db.list_conversations()

            for convo in conversations:
                convo_id = convo[0]
                title = convo[1]
                created_at = convo[2]   # adjust index if your schema differs
                print(f"ID {convo_id}: '{title}' ({created_at})")
            continue


# Handle 'load N' command
        if user_input.lower().startswith("load "):
            conversation_id = int(user_input.split()[1])

            bot.load_conversation(conversation_id)

            print(f"Loaded conversation #{conversation_id}")

            continue


# Handle 'delete N' command
        if user_input.lower().startswith("delete "):
            conversation_id = int(user_input.split()[1])
            db.delete_conversation(conversation_id)
            print(f"Deleted conversation #{conversation_id}")
            continue
        
        # 2. EVAL — send to Claude, get response
        # Wrapped in try/except to catch API errors gracefully
        try:
            response = bot.chat(user_input)
            # 3. PRINT — show the response
            print(f"\nClaude: {response}\n")
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")
        
        # 4. LOOP — back to top, ask for next message


# This is the entry point — only runs main() if this file is executed directly
if __name__ == "__main__":
    main()