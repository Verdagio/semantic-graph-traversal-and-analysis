import os
from abc import ABC, abstractmethod
import openai
import ollama
from dotenv import load_dotenv

load_dotenv()

# Define the abstract base class for chat models
class ChatModel(ABC):
    @abstractmethod
    def chat(self, message: str) -> str:
        pass

# OpenAI GPT implementation
class OpenAILLM(ChatModel):
    def __init__(self, model_name: str) -> None:
        super().__init__()
        self.client = openai.OpenAI(api_key=str(os.getenv('LLM_API_KEY')))
        self.model_name = model_name
    
    def chat(self, messages) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content

    def fn_chat(self, messages, tools = None) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        return response
    
class OllamaLLM(ChatModel):
    
    def __init__(self, model_name: str) -> None:
        super().__init__()
        self.model_name = model_name

    def chat(self, messages) -> str:
        res = ollama.chat(self.model, messages)
        return res['message']['content']
        
# Chat application class
class LLM:
    def __init__(self, chat_model: ChatModel) -> None:
        self.model = chat_model
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        
    def set_system_message(self, message: str) -> None:
        self.messages = [{"role": "system", "content": message}] + self.messages[1:]
        
    def get_system_message(self) -> str:
        return self.messages[0]

    def chat(self, message: str, tools = None) -> str:
        """
        Chat function for the LLM class.

        Parameters:
        message (str): The message to be sent to the chat model.
        model (str, optional): The model to use for the chat. Defaults to None.
        tools (list, optional): The tools to use for the chat. Defaults to None. (Only works with OpenAILLM)

        Returns:
        str: The response from the chat model.
        """
        self.messages.append({"role": "user", "content": message})
        
        if tools is not None and isinstance(self.model, OpenAILLM):
            response = self.model.fn_chat(self.messages, tools)
            self.messages.append({"role": "assistant", "content": response.choices[0].message.content})
        else:
            response = self.model.chat(self.messages)
            self.messages.append({"role": "assistant", "content": response})

        return response



def llm_provider(model_name: str) -> ChatModel:
    if os.getenv('LLM_API_KEY') is not None and model_name in [model.id for model in openai.OpenAI(api_key=str(os.getenv('LLM_API_KEY'))).models.list()]:
        model = OpenAILLM(model_name)
    elif any([model['name'] for model in ollama.list()['models'] if model_name in model['name']]):
        model = OllamaLLM(model_name)

    if model is not None:
        return LLM(model)
    
    raise ValueError(f"Invalid LLM name: {model_name}")

# Example usage
if __name__ == "__main__":
    llm = llm_provider('gpt-4o')

    llm.set_system_message("You are a helpful assistant.")

    user_message = "Hello, how are you?"
    # response = llm.chat(user_message, tools=tools)
    response = llm.chat(user_message)
    print(response)
