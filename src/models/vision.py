from huggingface_hub import InferenceClient

class VisionModel:
    PATH = "meta-llama/Llama-3.2-11B-Vision-Instruct"
    
    def __init__(self, token: str) -> None:
        self.__client = InferenceClient(api_key=token)
    
    ...
