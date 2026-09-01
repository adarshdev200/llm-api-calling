from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ChatMessage:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now) #"Whenever someone creates a ChatMessage without providing a timestamp, run the datetime.now machine and use its result."

    def __post_init__(self):
        if self.role not in ["user", "assistant", "system"]:
            raise ValueError(f"Invalid role: {self.role}")
    
    def to_api_format(self): 
        return {"role": self.role, "content": self.content}

@dataclass    
class Conversation :
    system_prompt: str = ""
    messages: list = field(default_factory=list)

    def add_user_message(self, content):
        self.messages.append(ChatMessage(role="user", content=content))
    
    def add_assistant_message(self, content):
        self.messages.append(ChatMessage(role="assistant", content=content))

    def to_api_format(self):
        result = []
        if self.system_prompt.strip() != "":
            result.append({"role": "system", "content": self.system_prompt})
        for msg in self.messages:
            result.append(msg.to_api_format())
        return result
    
    def clear(self):
        self.messages = []
    
    def __len__(self):
        return len(self.messages)
    
    def __str__(self):
        return str(self.messages)
