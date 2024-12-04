from huggingface_hub import InferenceClient
from typing import Optional

MARKDOWN_RULE = "WRITE IN MARKDOWN STYLE ONLY, DO NOT FORGET THAT YOUR MESSAGES ARE SENT TO TELEGRAM, WHICH CANNOT SHOW SOME ELEMENTS SUCH AS HEADS."

class LLM:
    def __init__(self, token: str) -> None:
        self.__client = InferenceClient(api_key=token)
    
    
    def question(
        self, 
        content: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        completion = self.__client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct", 
	        messages=self.to_message(content), 
	        max_tokens=max_tokens
        )
        return completion.choices[0].message.content


    def to_message(self, content: str):
        message = [
            {
	        	"role": "system",
	        	"content": MARKDOWN_RULE,
	        },
	        {
	        	"role": "user",
	        	"content": content,
	        }
        ]
        return message
    