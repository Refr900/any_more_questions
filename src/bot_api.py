from dataclasses import dataclass
import logging
from aiogram import F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
# from concurrent.futures import ProcessPoolExecutor
# from queue import Queue

from settings import Settings
from llm_api import LLM

class MyBot:
    def __init__(self, settings: Settings) -> None:
        self.bot = Bot(settings.bot_token)
        self.llm = LLM(settings.coder_token)
        # For now useless
        # self.pool = ProcessPoolExecutor(max_workers=settings.max_client)
        # self.queue = Queue(maxsize=settings.max_waiting_client)
    
    
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
        
        answer = self.get_answer(message.text)
        await temporary.delete()
        try:
            await message.reply(
                answer, 
                parse_mode=ParseMode.MARKDOWN,
            )
        except:
            logging.warning(f"failed reply to message({message.message_id}) in MARKDOWN")
            await message.reply(answer)
        logging.info(f"question by {message.from_user.full_name}({message.from_user.id}) complete!")
    
    
    def get_answer(self, question: str) -> str:
        # TODO: Add thread pool 
        return self.llm.ask_text_question(
            question, 
            # So now this hardcode value 
            max_tokens=1024
        )
    
    


