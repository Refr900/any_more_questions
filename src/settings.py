import os
import logging

class Settings:
    def load_from_env(self):
        if logging_level := os.getenv("LOGGING_LEVEL"):
            self.logging_level = logging_level
        else:
            self.logging_level = logging.ERROR
            
        self.bot_token = get_from_env("BOT_TOKEN")
        self.coder_token = get_from_env("CODER_TOKEN")
        self.vision_token = get_from_env("VISION_TOKEN")
        # For now useless
        # self.max_client = int(os.getenv("MAX_CLIENT"))
        # self.max_waiting_client = int(os.getenv("MAX_WAITING_CLIENT"))
    
    
def get_from_env(name: str) -> str:
    if var := os.getenv(name):
        return var
    else:
        raise RuntimeError(f"Not found `{name}` in environment!") 


def load_settings_from_env() -> Settings:
    settings = Settings()
    settings.load_from_env()
    return settings
