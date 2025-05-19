from datetime import datetime
from dataclasses import dataclass
import logging
from typing import Dict, List, Optional

from chatgpt_md_converter import telegram_format
import httpx

@dataclass
class User:
    id: int
    last_used: datetime
    uses_count: int
    dialog: List[Dict[str, str]]

@dataclass
class Answer:
    thinking: str | None
    text: str


async def llm_generate(
    inference_client, 
    token: str, 
    messages, 
    max_tokens: Optional[int] = 512
):
    try:
        return await free_generate(token, messages, max_tokens)
    except:
        logging.error("Free generation is run out :(")
        try:
            return await limit_generate(inference_client, messages, max_tokens)
        except:
            logging.error("Limit generation is too run out OMG")
            return Answer(None, None)
    

async def free_generate(token: str, messages, max_tokens: Optional[int] = 512):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        # "model": "deepseek/deepseek-v3-base:free",
        "model": "deepseek/deepseek-chat:free",
        "messages": messages,
        "max_tokens": max_tokens,
    }
    
    async with httpx.AsyncClient() as client:
        FREE_API = "https://openrouter.ai/api/v1/chat/completions"
        response = await client.post(FREE_API, json=data, headers=headers, timeout=(30.0, 30.0))

    if response.status_code == 200:
        data = response.json()
        if data['code'] == 429:
             raise RuntimeError("Rate limit exceeded")
        text = data["choices"][0]["message"]["content"]
    else:
        raise RuntimeError("Failed to fetch data from API")
    return deepseek_text_into_answer(text)


async def limit_generate(inference_client, messages, max_tokens: Optional[int] = 512):
    completion = await inference_client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        messages=messages,
        max_tokens=max_tokens,
    )
    text = completion.choices[0].message.content
    return deepseek_text_into_answer(text)

def deepseek_text_into_answer(text: str) -> Answer:
    chunks = list(text.split("</think>"))
    thinking = "<blockquote expandable><b>Thinking</b>\n" + chunks[0] + "</blockquote>"
    answer = telegram_format(chunks[1])
    return Answer(thinking, answer)