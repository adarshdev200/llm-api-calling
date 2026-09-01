from database import ChatDatabase

db = ChatDatabase()

conv_id = db.create_conversation(
    title="My first chat",
    system_prompt="You are helpful"
)
print(f"Created conversation {conv_id}")

db.save_message(conv_id, "user", "Hello!")
db.save_message(conv_id, "assistant", "Hi there!")
db.save_message(conv_id, "user", "How are you?")


messages = db.get_conversation_messages(conv_id)
print("\nMessages:")
for msg in messages:
    print(msg)

# List all conversations
print("\nAll conversations:")
for conv in db.list_conversations():
    print(conv)

db.close()