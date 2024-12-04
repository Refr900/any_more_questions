import os
from dotenv import load_dotenv 

class Settings:
    def load_from_env(self):
        load_dotenv()
        self.bot_token = os.getenv("BOT_TOKEN")
        self.llm_token = os.getenv("LLM_TOKEN")
        self.max_client = int(os.getenv("MAX_CLIENT"))
        self.max_waiting_client = int(os.getenv("MAX_WAITING_CLIENT"))


def load_settings() -> Settings:
    settings = Settings()
    settings.load_from_env()
    return settings
