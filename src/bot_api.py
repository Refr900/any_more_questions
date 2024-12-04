from dataclasses import dataclass
import threading
import logging
from aiogram import F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from settings import Settings
from llm_api import LLM
from concurrent.futures import ProcessPoolExecutor
from queue import Queue

class MyBot:
    def __init__(self, settings: Settings) -> None:
        self.bot = Bot(settings.bot_token)
        self.llm = LLM(settings.llm_token)
        self.pool = ProcessPoolExecutor(max_workers=settings.max_client)
        self.queue = Queue(maxsize=settings.max_waiting_client)
    
    
    async def start_polling(self):
        dp = Dispatcher()
        self.register_handles(dp)
        await dp.start_polling(self.bot)
    
    
    def register_handles(self, dp: Dispatcher):
        dp.message.register(self.cmd_start, Command("start"))
        dp.message.register(self.handle_question, F.text)
    
    
    async def cmd_start(self, message: Message):
        await message.reply("Да, старт. Спроси что-нибудь")


    async def handle_question(self, message: Message):
        logging.info(f"question by {message.from_user.full_name}({message.from_user.id})")
        temporary = await message.reply("Запрос принят, секунду :D")
        answer = self.add_question(message)
        await temporary.delete()
        await message.reply(answer)
        logging.info(f"question by {message.from_user.full_name}({message.from_user.id}) complete!")
    
    def get_answer(self, question: str) -> str:
        # TODO: Add thread pool 
        return self.llm.question(question, 500)
    
    


