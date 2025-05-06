from dotenv import load_dotenv
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import asyncio
import re
import pandas as pd
load_dotenv()

TELEGRAM_API_ID = int(os.getenv('app_api_id'))
TELEGRAM_API_HASH = os.getenv('app_api_hash')

client = TelegramClient("test", TELEGRAM_API_ID, TELEGRAM_API_HASH)
# WARNING: Not real-time! Just polling every X seconds

def scraper_classifier(job_details):
    url = job_details['link']
    if url.startswith("https://www.linkedin.com/jobs/view/"):
        return "linkedin"
    elif "myworkdayjobs.com" in url:
        return "workday"
    else:
        return "other job website"
    return




def message_regex(message):
    patterns = {
        "title": r"\s*\|\s*(.+)",
        "company": r"Empresa:\s*(.+)",
        "team": r"Equipo:\s*(.+)",
        "location": r"Ubicación:\s*(.+)",
        "experience_level": r"Nivel de experiencia:\s*(.+)",
        "link": r"(https?:\/\/[^\s]+)"
    }
    result = {
        key: (match := re.search(pattern, message)) and match.group(1)
        for key, pattern in patterns.items()
    }

    # Print only fields that were found
    for key, value in result.items():
        if value:
            print(f"{key.capitalize()}: {value}")

    # print(result)
    return result



async def poll_channel(channel_id):
    entity = await client.get_entity(PeerChannel(channel_id))
    last_message_id = ""
    while True:
        history = await client(GetHistoryRequest(
            peer=entity,
            limit=1,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))
        if history.messages:
            latest_message = history.messages[0]

            if latest_message.id != last_message_id:
                last_message_id = latest_message.id
                print("Last message:", history.messages[0].message)
                job_posting_data = message_regex(history.messages[0].message)
                print(scraper_classifier(job_posting_data))


        await asyncio.sleep(10)

async def main():
    await poll_channel(1771924936)

with client:
    client.loop.run_until_complete(main())