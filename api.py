from fastapi import FastAPI
from dotenv import load_dotenv
from providers import AnthropicProvider, MockProvider
from chatbot import ChatBot
from database import ChatDatabase
import os
from pydantic import BaseModel
from fastapi import HTTPException
import anthropic


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


def conversation_exists(user_id, conversation_id) :
        result = db.get_user_specific_convo(user_id=user_id)
        
        if conversation_id in [row[0] for row in result]:
            return True
        else:
            return False


@app.post("/chat/{user_id}/{conversation_id}")
def continue_chat(user_id: int, conversation_id: int, chatinput: chat):
    
    result = conversation_exists(user_id=user_id , conversation_id=conversation_id) 
    
    if result == True :
        bot = ChatBot(
            provider=provider,
            database=db,
            user_id=user_id,
            conversation_id=conversation_id,
            system_prompt="You are a friendly tutor")
        
        x = provider.validate_prompt(prompt=chatinput.input) 
        
        """
        This type of validaiton should not be performed from provider side it should be endpoint level validation 
        a better practice 
        """
        
        
        if x == True :
            try : 
                response = bot.chat(chatinput.input)
                
            except anthropic.AuthenticationError:
                raise HTTPException(status_code=500, detail="server configuration error") # Notice: you would NOT tell the caller "invalid API key" — that leaks your internal problem to them. Say something generic.

            except anthropic.RateLimitError:
                raise HTTPException(status_code=503, detail="service busy, try again shortly")
            
            except anthropic.APIStatusError:
                raise HTTPException(status_code=503, detail="model service unavailable")
                    
            return {
                "conversation_id": conversation_id,
                "response": response
            }
        
        else :
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
    else : 
        raise HTTPException(status_code=404 , detail="Convo not found")
            

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


    
@app.get("/conversations/list/{user_id}")
def list_conversations(user_id: int):
    conversations = db.get_user_specific_convo(user_id)
    return conversations

#For testing purpose

@app.get("/hello") 
def start() :
    return "Hello"

