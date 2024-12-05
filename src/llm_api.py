from huggingface_hub import InferenceClient
from typing import Optional

from models.coder import CoderModel

class LLM:
    def __init__(self, token: str) -> None:
        self.coder = CoderModel(token)
    
    
    def ask_text_question(
        self,
        content: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        return self.coder.ask_question(
            content=content,
            max_tokens=max_tokens,
        )