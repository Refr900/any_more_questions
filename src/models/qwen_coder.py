from typing import Dict, List, Optional
from huggingface_hub import InferenceClient

class QwenCoder:
    PATH = "Qwen2.5-Coder-32B-Instruct"
    FULL_PATH = "Qwen/Qwen2.5-Coder-32B-Instruct"
    
    def __init__(self, token: str) -> None:
        self.__client = InferenceClient(api_key=token, model=self.FULL_PATH)
    
    
    def answer_question(
        self, 
        messages: List[Dict[str, str]],
        content: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        messages = messages.copy()
        messages.extend([
            {
                "role": "system",
                "content": "You are an assistant who helps with checking information and searching for it. You are friendly and critical of information that may not be true. You should think step-by-step."
            },
            {
                "role": "user", 
                "content": content
            },
        ])
        
        completion = self.__client.chat_completion(
	        messages=messages, 
	        max_tokens=max_tokens,
        )
        
        return completion.choices[-1].message.content
    
    
    def can_answer_question(self) -> bool:
        return True
