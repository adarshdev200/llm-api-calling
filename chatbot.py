from conversation import Conversation

class ChatBot:

    def __init__(
        self,
        provider,
        database,
        user_id,
        system_prompt="",
        title="New Chat",
        conversation_id=None
    ):

        self.provider = provider
        self.db = database
        self.user_id = user_id

        self.conversation = Conversation(
            system_prompt=system_prompt
        )

        # If no conversation ID is provided,
        # create a brand-new conversation
        if conversation_id is None:

            self.conversation_id = self.db.create_conversation(
                title,
                system_prompt,
                user_id
            )

        # Otherwise, load the existing conversation
        else:

            self.conversation_id = conversation_id

            messages = self.db.get_conversation_messages(
        conversation_id,
        user_id
    )
            

            print("USER ID:", user_id)
            print("CONVERSATION ID:", conversation_id)
            print("LOADED MESSAGES:", messages)

            for row in messages:

                role = row[4]
                content = row[3]

                print("LOADING:", role, content)

                if role == "user":
                    self.conversation.add_user_message(content)

                elif role == "assistant":
                    self.conversation.add_assistant_message(content)
        
        
    
    def chat(self, user_input):
        self.conversation.add_user_message(user_input)
        self.db.save_message(self.conversation_id,"user",user_input)
        messages = self.conversation.to_api_format()
        response = self.provider.generate(messages)
        self.db.save_message(self.conversation_id,"assistant",response)
        return response
    
    
    def show_history(self):
        for msg in self.conversation.messages:
            time_str = msg.timestamp.strftime("%H:%M")
            print(f"[{msg.role} @ {time_str}]: {msg.content}")
    
    def reset(self):
        self.conversation.clear()


    def load_conversation(self, conversation_id):
        new_convo = self.db.get_conversation_messages(conversation_id,self.user_id)
        self.conversation.clear()

        self.conversation_id = conversation_id    
        
        for row in new_convo:
            role = row[4]
            content = row[3]
            if role == "user":
                self.conversation.add_user_message(content)
            elif role == "assistant":
                self.conversation.add_assistant_message(content)
