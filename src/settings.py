import os
from dotenv import load_dotenv 

class Settings:
    def load_from_env(self):
        load_dotenv()
        self.bot_token = os.getenv("BOT_TOKEN")
        self.llm_token = os.getenv("LLM_TOKEN")
        self.max_client = int(os.getenv("MAX_CLIENT"))
        self.max_waiting_client = int(os.getenv("MAX_WAITING_CLIENT"))
        if self.max_client < self.max_waiting_client:
            raise SettingsError(self.max_client, self.max_waiting_client)


def load_settings() -> Settings:
    settings = Settings()
    settings.load_from_env()
    return settings


class SettingsError(Exception):
    def __init__(
        self,
        max_client: int,
        max_waiting_client: int,
    ):
        message = f"MAX_CLIENT({max_client}) must be greater than MAX_WAITING_CLIENT({max_waiting_client})."
        super().__init__(message)