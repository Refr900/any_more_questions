import logging
import asyncio
from dotenv import load_dotenv 

from bot_api import MyBot 
from settings import load_settings_from_env


async def main():
    load_dotenv()
    settings = load_settings_from_env()
    logging.basicConfig(level=settings.logging_level)
    bot = MyBot(settings)
    await bot.start_polling()
    

if __name__ == "__main__":
    asyncio.run(main())