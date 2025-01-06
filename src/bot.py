from concurrent.futures import ThreadPoolExecutor

import asyncio
from datetime import datetime
import logging
from aiogram import F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command

from db import User
from settings import Settings

from models.qwq import QwQ
from models.qwen_coder import QwenCoder

class MyBot:
    def __init__(self, loop, settings: Settings) -> None:
        self.bot = Bot(settings.bot_token)
        self.models = {
            QwenCoder.PATH: QwenCoder(settings.coder_token),
            QwQ.PATH: QwQ(settings.coder_token),
        }
        self.loop = loop
        self.users = {}
        self.uses_count = 0
        self.client_count = 0
        self.max_client_count = settings.max_client_count
        self.free_uses_count = settings.free_uses_count
        self.all_free_uses_count = settings.all_free_uses_count
        self.uses_span = settings.uses_span
    
    
    async def start_polling(self):
        dp = Dispatcher()
        dp.message.register(self.cmd_start, Command("start"))
        dp.message.register(self.cmd_account, Command("account"))
        dp.message.register(self.handle_question, F.text)
        await dp.start_polling(self.bot)
    
    
    async def cmd_start(self, message: Message):
        await message.reply("Да, старт. Спроси что-нибудь")
    
    
    async def cmd_account(self, message: Message):
        user = self.get_user(message.from_user.id)
        await message.reply(
            f"Запросов в день: {user.uses_count}/{self.free_uses_count}\n- {user.model}"
        )

    async def handle_question(self, message: Message):
        logging.info(f"question by {message.from_user.username}({message.from_user.id})")
        
        user = self.get_user(message.from_user.id)
        
        if user.uses_count >= self.free_uses_count:
            await message.reply("Бесплатные запросы кончились, ждите следующего дня")
            return
        
        if not self.can_ask():
            await message.reply("Бесплатные запросы кончились для всех, ждите следующего дня")
            return
        
        if self.is_full():
            await message.reply("К сожалению, в данный момент высокая нагрузка, попробуйте позже")
            return

        if time_difference(user.last_used) < self.uses_span:
            await message.reply("Не так быстро, подождите еще пару секунд")
            return
        
        user.uses_count += 1
        user.last_used = datetime.now()
        
        self.client_count += 1
        self.uses_count += 1
        
        reply_temporary = asyncio.create_task(
            self.bot(message.reply("Запрос принят, секунду... "))
        )
        
        send_question = asyncio.create_task(
            self.answer_question(user, message.text)
        )
        
        temporary = await reply_temporary
        answer = await send_question
        
        try:
            delete_temporary = asyncio.create_task(
                self.bot(temporary.delete())
            )
            reply_question = asyncio.create_task(
                self.bot(message.reply(
                    answer,
                    parse_mode=ParseMode.MARKDOWN,
                ))
            )
            await delete_temporary
            await reply_question
        except:
            logging.warning(f"failed reply to message({message.message_id}) in MARKDOWN")
            await message.reply(send_question)
        
        while len(user.dialog) >= 8:
            user.dialog = user.dialog[2:]
   
        user.dialog.append(
            {
                "role": "user", 
                "content": message.text
            },
        )
        
        user.dialog.append(
            {
                "role": "assistant", 
                "content": answer
            }
        )
       
        self.client_count -= 1
    
    
    async def answer_question(self, user: User, question: str) -> str:
        model = self.models.get(user.model)
        if model == None:
            raise RuntimeError("Cannot found model!")
        
        if not model.can_answer_question():
            raise RuntimeError("The model cannot answer the question!")
             
        with ThreadPoolExecutor(max_workers=1) as pool:
            return await self.loop.run_in_executor(
                pool,
                model.answer_question,
                # messages
                user.dialog,
                # content
                question,
                # max_tokens
                512
            )
    
    
    def can_ask(self) -> bool:
        return self.uses_count <= self.all_free_uses_count 
    
    
    def is_full(self) -> bool:
        return self.client_count == self.max_client_count
    
    
    def get_user(self, id: int) -> User:
        if self.users.get(id) == None:
            self.add_user(id)
        return self.users[id]
    
    
    def add_user(self, id: int):
        self.users[id] = User(
            id=id, 
            model=QwenCoder.PATH, 
            last_used=datetime.min, 
            uses_count=0, 
            dialog=[]
        ) 
        

def time_difference(datetime: datetime) -> float:
    return (datetime.now() - datetime).total_seconds()