import logging
import datetime

from aiogram import md
from aiogram.types import Message
from googlesearch import search as google_search
from markdownify import markdownify
from chromadb import Collection
import chromadb
from ollama import AsyncClient
from aiogram.enums import ParseMode
import requests

from db import free_generate, llm_generate
from embeddings import create_embeddings
import embeddings

NUM_RESULTS = 8

async def search(
    inference_client, 
    token: str, 
    client: AsyncClient, 
    collection: Collection, 
    message: Message
) -> list[str]:
    query = await create_query(inference_client, token, message.text)
    if query == None:
        return []
    
    extra = []
    search_msg = await message.answer(
        text=md.bold("Поиск 🔎"),
        parse_mode=ParseMode.MARKDOWN,
    )
    
    try:  
        sites = google_search(
            query, 
            num_results=NUM_RESULTS, 
            advanced=True,
            unique=True,
        )
        
        for site in sites:
            try:
                # text = md.bold("Читаем ") + md.link(site.title, site.url)
                # temp = await message.reply(
                #     text=text,
                #     parse_mode=ParseMode.MARKDOWN, 
                #     link_preview_options=LinkPreviewOptions(
                #         is_disabled=True,
                #         # show_above_text=True
                #     ),
                # )
                # temps.append(temp)
                
                logging.info(f"site: {site.url}")
                source = requests.get(site.url, timeout=(2.0, 2.0)).content
                source = markdownify(source.decode())[:embeddings.EMBED_DEPTH]
                await create_embeddings(
                    client=client,
                    collection=collection,
                    id=site.url,
                    source=source,
                )
            except Exception as e:
                logging.error(f"EMBEDDING: {e}")
        
        
        extra = await embeddings.search(client, collection, query)
        await search_msg.delete()
    except Exception as e:
        logging.error(f"RAG: {e}")
    chromadb.api.client.SharedSystemClient.clear_system_cache()
    
    
    
    now = datetime.datetime.now()
    extra.append(f"Current time: {now}")
    return extra


async def create_query(inference_client, token, message) -> str:
    answer = await llm_generate(
        inference_client=inference_client,
        token=token, 
        messages=[
            {
                "role": "user",
                "content": rag_format(message),
            },
        ]
    )
    return answer.text


def rag_format(message):
    return ("Formulate a short and precise query for the search engine. "
            "If the question does not require searching, answer \"SEARCH_NOT_REQUIRED\" but without quotation marks.\n" 
            "if the question is trivial, search is not needed."
            "If you are asked to search on the Internet, then search."
            "\n"
            "Examples:\n" 
            "What the last version of python? => python last version\n"
            "What the weather in the Moscow? => Moscow weather\n" 
            "How are you, my friend? => SEARCH_NOT_REQUIRED\n"
            "Can elephants fly? => SEARCH_NOT_REQUIRED\n"
            "Write the esse about sense of life => SEARCH_NOT_REQUIRED\n"
            "Write the esse about sense of life, using search in internet => sense of life\n"
            "\n"
            "If you need to find or check something, you need to search, for example, check the news"
            "\n"
            ) + message