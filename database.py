import sqlite3
from datetime import datetime
import os


class ChatDatabase:
    def __init__(self, db_path="chatbot.db"):

        self.db_path = db_path

        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False
        )
        
        print("DB PATH:", os.path.abspath(db_path))
        print("DB READONLY:", self.conn.execute("PRAGMA query_only").fetchone())
        
        print("DATABASE PATH:", os.path.abspath("chatbot.db"))

        self.conn.execute("PRAGMA foreign_keys = ON")

        self.cursor = self.conn.cursor()

        self._create_tables()
  
    
    def _create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT
        )
    """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            system_prompt TEXT,
            title TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            conversation_id INTEGER,
            content TEXT,
            role TEXT,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
    """)
        self.conn.commit()
    
    def create_conversation(self, title, system_prompt, user_id):
        """Creates a new conversation. Returns the new conversation_id."""
        self.cursor.execute("""
                            INSERT INTO conversations (title, system_prompt,user_id)
                            VALUES (?, ?, ?)
                            """, (title, system_prompt,user_id))

        self.conn.commit()
        return self.cursor.lastrowid


    def save_message(self, conversation_id, role, content):

        print("SAVING MESSAGE:")
        print("conversation_id =", conversation_id)
        print("role =", role)
        print("content =", content)

        self.cursor.execute("""
        INSERT INTO messages (conversation_id, role, content)
        VALUES (?, ?, ?)
    """, (conversation_id, role, content))

        self.conn.commit()

        print("MESSAGE SAVED")

    
    def get_conversation_messages(self, conversation_id, user_id):

        print("LOOKING FOR:")
        print("conversation_id =", conversation_id)
        print("user_id =", user_id)

        self.cursor.execute("""
        SELECT id, user_id
        FROM conversations
        WHERE id = ?
    """, (conversation_id,))

        conversation = self.cursor.fetchone()

        print("CONVERSATION FOUND:", conversation)

        self.cursor.execute("""
        SELECT *
        FROM messages
        WHERE conversation_id = ?
    """, (conversation_id,))

        messages = self.cursor.fetchall()

        print("MESSAGES FOUND:", messages)

        self.cursor.execute("""
        SELECT messages.*
        FROM messages
        JOIN conversations
        ON messages.conversation_id = conversations.id
        WHERE messages.conversation_id = ?
        AND conversations.user_id = ?
        ORDER BY messages.created_at
    """, (conversation_id, user_id))

        final_messages = self.cursor.fetchall()

        print("FINAL RESULT:", final_messages)

        return final_messages
    
    
    def debug_messages(self):

        print("USERS:")
        self.cursor.execute("SELECT * FROM users")
        print(self.cursor.fetchall())

        print("CONVERSATIONS:")
        self.cursor.execute("SELECT * FROM conversations")
        print(self.cursor.fetchall())

        print("MESSAGES:")
        self.cursor.execute("SELECT * FROM messages")
        print(self.cursor.fetchall())
       
        
    
    def close(self):
        # TODO 19: self.conn.close()
        self.conn.close()

    def delete_conversation(self, conversation_id, user_id):

    # First delete messages only if the conversation belongs to this user
        self.cursor.execute("""
        DELETE FROM messages
        WHERE conversation_id = ?
        AND conversation_id IN (
            SELECT id
            FROM conversations
            WHERE id = ? AND user_id = ?
        )
    """, (conversation_id, conversation_id, user_id))

    # Delete conversation only if owned by this user
        self.cursor.execute("""
        DELETE FROM conversations
        WHERE id = ?
        AND user_id = ?
    """, (conversation_id, user_id))

        self.conn.commit()


    def get_user_specific_convo(self, user_id):
        self.cursor.execute("""
            
            SELECT id , created_at, title FROM conversations
            WHERE user_id = ?
            ORDER BY created_at DESC""", (user_id,))
        
        return self.cursor.fetchall()

    def create_user(self, username):

        print("CREATE USER CALLED")
        print("DB PATH:", self.db_path)
        print("QUERY ONLY:", self.conn.execute("PRAGMA query_only").fetchone())

        self.cursor.execute("""
        INSERT INTO users (username)
        VALUES (?)
    """, (username,))

        self.conn.commit()

        print("CREATE USER INSERT WORKED")

        return self.cursor.lastrowid