from huggingface_hub import InferenceClient
from typing import Optional


class LLM:
    def __init__(self, token: str) -> None:
        self.__client = InferenceClient(api_key=token)
    
    
    def question(
        self, 
        content: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        messages = [
	        {
	        	"role": "user",
	        	"content": content,
	        }
        ]
        completion = self.__client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct", 
	        messages=messages, 
	        max_tokens=max_tokens
        )
        return completion.choices[0].message.content
