from huggingface_hub import InferenceClient
from typing import Optional

class CoderModel:
    PATH = "Qwen/Qwen2.5-Coder-32B-Instruct"
    
    def __init__(self, token: str) -> None:
        self.__client = InferenceClient(api_key=token, model=self.PATH)
    
    
    def ask_question(
        self, 
        content: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        completion = self.__client.chat.completions.create(
	        messages=self.to_messages(content), 
	        max_tokens=max_tokens,
            temperature=0.1,
        )
        return completion.choices[0].message.content


    def to_messages(self, content: str):
        messages = [
            {
                "role": "user", 
                "content": content
            },
        ]
        return messages