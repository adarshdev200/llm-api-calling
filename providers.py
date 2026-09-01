import os
from anthropic import Anthropic

class LLMProvider : 
    provider_name = "base"

    def __init__(self, model, temperature, api_key):
        self.model = model
        self.temperature = temperature
        self._api_key = api_key

    @property
    def masked_key(self) :
        if not self._api_key :
            return "No key found"
        return f"{self._api_key[:5]}...{self._api_key[-4:]}"
    
    def _validate_prompt(self,prompt) :
        if prompt.strip() == "" :
            raise ValueError("Prompt cannot be empty")
        
    def generate(self, messages):
        raise NotImplementedError("Subclasses must implement generate()")
    
# ----------------------------------------------------------------------------------


class AnthropicProvider(LLMProvider):
    provider_name = "anthropic"
    
    def __init__(self, model="claude-sonnet-4-5", temperature=0.7, api_key=None, max_tokens=1024):
        super().__init__(model,temperature,api_key)
        self.max_tokens = max_tokens
        self._client = Anthropic(api_key=api_key)

    
    def generate(self, messages):
        """
        messages: a list of dicts in the format [{"role": "user", "content": "..."}]
                  (this is what conversation.to_api_format() returns, minus system)
        Returns: the assistant's response as a string
        """

        system_text = ""
        chat_messages = []
        for msg in messages : 
            if msg["role"] == "system" :
                system_text = msg["content"]
            else :
                chat_messages.append(msg)


        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_text,        # optional, only if you have one
            messages=chat_messages
        )
        return response.content[0].text
        


class MockProvider(LLMProvider):
    provider_name = "mock"
    
    def __init__(self, model="mock", temperature=0.0, api_key="fake"):
        super().__init__(model, temperature, api_key)
    
    def generate(self, messages):
        # Returns a fake response — useful for testing without API costs
        last_user_msg = messages[-1]["content"] if messages else "nothing"
        return f"[Mock response to: '{last_user_msg}']"