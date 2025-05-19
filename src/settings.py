import os
import logging

class Settings:
    def load_from_env(self):
        if logging_level := os.getenv("LOGGING_LEVEL"):
            self.logging_level = logging_level
        else:
            self.logging_level = logging.ERROR
            
        self.bot_token = get_from_env("BOT_TOKEN")
        self.inference_token = get_from_env("INFERENCE_TOKEN")
        self.free_model_token = get_from_env("FREE_MODEL_TOKEN")
        self.max_client_count = int(get_from_env("MAX_CLIENT_COUNT"))
        self.free_uses_count = int(get_from_env("FREE_USES_COUNT"))
        self.uses_span = float(get_from_env("USES_SPAN"))
    
    
def get_from_env(name: str) -> str:
    if var := os.getenv(name):
        return var
    else:
        raise RuntimeError(f"Not found `{name}` in environment!") 


def load_settings_from_env() -> Settings:
    settings = Settings()
    settings.load_from_env()
    return settings
