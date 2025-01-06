from huggingface_hub import AsyncInferenceClient

class VisionModel:
    PATH = "meta-llama/Llama-3.2-11B-Vision-Instruct"
    
    def __init__(self, token: str) -> None:
        self.__client = AsyncInferenceClient(api_key=token)
