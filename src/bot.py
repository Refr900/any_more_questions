from typing import Dict, List, Optional

from chatgpt_md_converter import telegram_format

import chromadb
from markdownify import markdownify
from ollama import AsyncClient, Options
from huggingface_hub import AsyncInferenceClient

from datetime import datetime
import logging
from aiogram import F, Bot, Dispatcher, html, md
from aiogram.types import Message, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram.filters import Command

from db import Answer, User, free_generate, llm_generate
import rag
from settings import Settings

STEP_LIMIT = 4000
FREE_API = "https://openrouter.ai/api/v1/chat/completions"

class MyBot:
    def __init__(self, loop, settings: Settings) -> None:
        self.bot = Bot(settings.bot_token)
        self.model_client = AsyncClient()
        self.free_model_token = settings.free_model_token
        self.inference_client = AsyncInferenceClient(
            provider="hf-inference",
        	api_key=settings.inference_token,
        )
        
        self.loop = loop
        self.users = {}
        
        # Rate limits
        self.client_count = 0
        self.max_client_count = settings.max_client_count
        self.free_uses_count = settings.free_uses_count
        self.uses_span = settings.uses_span
    
    
    async def start_polling(self):
        dp = Dispatcher()
        dp.message.register(self.cmd_start, Command("start"))
        dp.message.register(self.cmd_account, Command("account"))
        dp.message.register(self.cmd_clear, Command("clear"))
        dp.message.register(self.handle_question, F.text)
        await dp.start_polling(self.bot)
    
    
    async def cmd_start(self, message: Message):
        await message.reply("Да, старт. Спроси что-нибудь")
    
    
    async def cmd_account(self, message: Message):
        user = self.get_user(message.from_user.id)
        await message.reply(
            f"Запросов в день: {user.uses_count}/{self.free_uses_count}\n"
        )
    
    
    async def cmd_clear(self, message: Message):
        user = self.get_user(message.from_user.id)
        user.dialog.clear()
        await message.reply("Контекст удален")
    

    async def handle_question(self, message: Message):
        self.client_count += 1
        try:
            await self.question_inner(message)
        except Exception as e:
            logging.error(f"failed request for user({message.from_user.id}): {e}")
            await message.reply("Что-то пошло не так...")
        self.client_count -= 1
    
    
    async def question_inner(self, message: Message):
        logging.info(f"question by {message.from_user.username}({message.from_user.id})")
        user = self.get_user(message.from_user.id)
        
        # Checking rate limits 
        if user.uses_count >= self.free_uses_count:
            await message.reply("Бесплатные запросы кончились, ждите следующего дня")
            return
          
        if self.is_full():
            await message.reply("В данный момент высокая нагрузка, попробуйте позже")
            return

        remaining = self.uses_span - elapsed(user.last_used)
        if remaining > 0:
            await message.reply(f"Не так быстро, подождите еще {remaining:.1f}s")
            return
        
        user.last_used = datetime.now()
        
        temporary = await message.reply("Запрос принят, минуту... или больше в зависимости от вопроса")
        # Answer question
        answer = await self.chat_with_user(user, message)
        await temporary.delete()

        if answer.text == None:
            await message.reply("Достигнут лимит генерации 😔\n\nБудет восстановлен через ближайщие 24 часа, наверное 😎")
        elif answer.text == "":
            temporary = await message.reply("Требуется больше времени, чем ожидалось...")
            answer = await self.chat_with_user(user, message)
            if answer.text == "" or answer.text == None:
                await message.reply("Большая нагрузка, попробуйте снова позже :(")
            await temporary.delete()
        
        # Send answer
        if answer.text != None:
            await self.send_message(message, answer)
            # await message.reply(f"Заняло {elapsed(user.last_used):.1f}s")
        
        # Delete old messages
        while len(user.dialog) >= 8:
            user.dialog = user.dialog[2:]

        # Add new messages
        user.dialog.append(
            {
                "role": "user", 
                "content": message.text
            },
        )
        
        user.dialog.append(
            {
                "role": "assistant", 
                "content": answer.text
            }
        )

    async def send_message(self, message, answer):
        if thinking := answer.thinking:
            if len(thinking) + len(answer.text) > STEP_LIMIT:
                await self.reply_expandable_blockquote(message, thinking)
                await self.reply(message, answer.text)
            else:
                await self.reply(message, html.expandable_blockquote(thinking) + answer.text)
        else:
            await self.reply(message, answer.text)

    async def reply(self, message: Message, text):
        for i in range(0, len(text), STEP_LIMIT):
            chunk = text[i:i + STEP_LIMIT]
            try:
                await message.reply(chunk, parse_mode=ParseMode.HTML, link_preview_options=LinkPreviewOptions(prefer_small_media=True))
            except Exception as e:
                logging.error(f"failed reply with `parse_mode=HTML` for user({message.from_user.id}): {e}")
                await message.reply(chunk)
    
    
    async def reply_expandable_blockquote(self, message, text):
        for i in range(0, len(text), STEP_LIMIT):
            chunk = html.expandable_blockquote(text[i:i + STEP_LIMIT])
            try:
                await message.reply(chunk, parse_mode=ParseMode.HTML)
            except Exception as e:
                logging.error(f"failed reply with `parse_mode=HTML` for user({message.from_user.id}): {e}")
                await message.reply(chunk)
    
    
    async def chat_with_user(self, 
        user: User, 
        message: Message, 
        max_tokens: Optional[int] = 2048
    ) -> Answer:
        logging.info(f"use chat_free")
        
        logging.info("search with rag")
        extra = await self.search_with_rag(message)
        
        user.dialog.extend([
            {
                "role": "user",
                "content": f"RAG SYSTEM: {{{extra}}}. " + self.format_with_system(f" USER: {message.text}"), 
            },
        ])
        
        answer_msg = await message.answer(
            text=md.bold("Отвечаем 📝"),
            parse_mode=ParseMode.MARKDOWN,
        )
        
        logging.info("generate answer")
        answer = await llm_generate(
            self.inference_client, 
            self.free_model_token, 
            user.dialog, 
            max_tokens,
        )
        
        user.dialog = user.dialog[:-1]
        await answer_msg.delete()
        return answer
    

    async def search_with_rag(self, message: Message) -> list[str]:
        client = chromadb.Client()
        collection = client.create_collection(name="documents", get_or_create=True)
        data = await rag.search(self.inference_client, self.free_model_token, self.model_client, collection, message)        
        if len(collection.get()["ids"]) > 0:
            collection.delete(collection.get()["ids"])
        return data
    
    
    async def chat_local(
        self,
        messages: List[Dict[str, str]],
        content: str,
        max_tokens: Optional[int],
    ) -> Answer:
        raise RuntimeError("todo")
    
        # * Создаем базу
        client = chromadb.Client()
        collection = client.create_collection(name="documents", get_or_create=True)
        # * Ищем 
        extra = await rag.search(self.model_client, collection, content)
        print(extra)
        
        if len(collection.get()["ids"]) > 0:
            collection.delete(collection.get()["ids"])
                
        # Getting answer
        messages.extend([
            {
                "role": "system",
                "content": self.system(),
            },
            {
                "role": "user",
                "content": f"RAG SYSTEM: {{{extra}}}. USER: {content}",
            }
        ])
        
        response = await self.model_client.chat(
            model="bambucha/saiga-llama3:8b",
            messages=messages,
            options=Options(
                num_predict=max_tokens,
            ),
        )
        answer = response.message.content
        # Clean up
        messages = messages[:-2]
        
        # Convert into telegram style
        # chunks = list(answer.split("</think>"))
        # thinking = chunks[0].replace("<think>", "<b>Thinking</b>")
        # thinking = chunks[0].replace("<think>", "<blockquote expandable><b>Thinking</b>") + "</blockquote>"
        # answer = telegram_format(chunks[-1])
        answer = telegram_format(answer)
        
        # async with Translator() as translator:
            # translate = await translator.translate(answer, dest="ru")
            # answer = translate.text
        
        return Answer(None, answer)
    
    def format_with_system(self, content: str) -> str:
        return self.system() + content
    
    def system(self) -> str:
        return (
                "You are the best assistant for searching and checking information, you don't use emojis. "
                "You have up-to-date data thanks to the RAG system."
                # "If the question is complex you first give a short answer in two to five phrases, then write everything down point by point (3-5) and sum it up, use **bold** text for main ideas. Divide text into paragraphs (more is better)"
                # "If the question is easy, answer immediately. Tell at least one phrase. "
                "Use TELEGRAM MARKDOWN for links and other stuff. Be careful in this case, please. "
                "LaTeX not work in telegram, not use LaTeX, please. "
                # "Instead of headings, just use bold text\nExample: ### Top Languages ​​​​=> **Top Languages**\n"
                "Please note which sites you are taking data from, if any."
                )
    
    def is_full(self) -> bool:
        return self.client_count == self.max_client_count + 1
    
    
    def get_user(self, id: int) -> User:
        if self.users.get(id) == None:
            self.add_user(id)
        return self.users[id]
    
    
    def add_user(self, id: int):
        self.users[id] = User(
            id=id,
            last_used=datetime.min,
            uses_count=0,
            dialog=[]
        ) 


def elapsed(datetime: datetime) -> float:
    return (datetime.now() - datetime).total_seconds()