from fastapi import FastAPI
from dotenv import load_dotenv
from providers import AnthropicProvider, MockProvider
from chatbot import ChatBot
from database import ChatDatabase
import os
from pydantic import BaseModel


app = FastAPI()

class chat(BaseModel):   #using pydantic here 
    input : str

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("No ANTHROPIC_API_KEY found in .env file!")

provider = AnthropicProvider(api_key=API_KEY)
db = ChatDatabase()

# This is for continuing conversartion

@app.post("/chat/{user_id}/{conversation_id}")
def continue_chat(user_id: int, conversation_id: int, chatinput: chat):

    bot = ChatBot(
        provider=provider,
        database=db,
        user_id=user_id,
        conversation_id=conversation_id,
        system_prompt="You are a friendly tutor"
    )

    response = bot.chat(chatinput.input)
    db.debug_messages()

    return {
        "conversation_id": conversation_id,
        "response": response
    }
    
    
# @app.post('/chat/intial/{user_id}/{conversation_id}')
# def intial_chat(user_id: int, conversation_id: int, chatinput: chat) :
    
#         bot = ChatBot(
#         provider=provider,
#         database=db,
#         user_id=user_id,
#         conversation_id=conversation_id,
#         system_prompt="You are a friendly tutor"
#     )

#         response = bot.chat(chatinput.input)
    
    



# This endpoint is for new users to create a db entry
    

@app.post("/users")
def create_user():

    user_id = db.create_user("Adarsh")

    return {
        "user_id": user_id
    }

# this is for users existing in DB and wants to start a conversation


@app.post("/conversations/{user_id}")
def create_new_conversation(user_id: int):
    
    
    bot = ChatBot(provider=provider,
                  database=db,
                  user_id=user_id,
                  system_prompt='You are a friendly tutor',
                  title="New chat"
                  )
    return {
        "conversation_id": bot.conversation_id
    }
    
#this is to list all the conversations


    
@app.get("/conversations/{user_id}")
def list_conversations(user_id: int):
    conversations = db.get_user_specific_convo(user_id)
    return conversations

