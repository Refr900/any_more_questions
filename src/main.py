import logging
import asyncio

from bot_api import MyBot 
from settings import load_settings


def init_logger():
    logging.basicConfig(level=logging.INFO)


async def main():
    init_logger()
    bot = MyBot(load_settings())
    await bot.start_polling()
    

if __name__ == "__main__":
    asyncio.run(main())