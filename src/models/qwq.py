from typing import Optional
from huggingface_hub import InferenceClient

class QwQ:
    PATH = "QVQ-72B-Preview"
    FULL_PATH = "Qwen/QVQ-72B-Preview"
    
    def __init__(self, token: str) -> None:
        self.__client = InferenceClient(api_key=token, model=self.FULL_PATH)
    
    
    def answer_question(
        self,
        content: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        text = {
        	"type": "text",
        	"text": content
        }
        
        message = {
        	"role": "user",
        	"content": [text]
        }
                
        completion = self.__client.chat_completion(
	        messages=[message], 
	        max_tokens=max_tokens,
        )
        
        return completion.choices[0].message.content
    
    
    def can_answer_question(self) -> bool:
        return True
