import logging
import asyncio
from dotenv import load_dotenv 

from bot import MyBot 
from settings import load_settings_from_env


async def main():
    load_dotenv()
    settings = load_settings_from_env()
    logging.basicConfig(level=settings.logging_level) 
    loop = asyncio.get_event_loop()
    bot = MyBot(loop, settings)
    await bot.start_polling()


if __name__ == "__main__":
    asyncio.run(main())

