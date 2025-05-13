from dotenv import load_dotenv
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import asyncio
import re
from src.core.llm import get_model_response
from src.core.prompt_manager import get_prompt_template_from_jinja2
import pandas as pd
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.scrapers.workday_scraper import WorkdayScraper
from src.core.assess_profile import assess_user
from src.core.generate_resume import generate_resume
from src.core.save_results import save_results
from settings import FILTER_JOBS_KEYWORDS, JOB_TYPE_TARGETS
load_dotenv()

TELEGRAM_API_ID = int(os.getenv('app_api_id'))
TELEGRAM_API_HASH = os.getenv('app_api_hash')

client = TelegramClient("test", TELEGRAM_API_ID, TELEGRAM_API_HASH)
# WARNING: Not real-time! Just polling every X seconds

def scraper_classifier(job_details):
    url = job_details['link']
    if url.startswith("https://www.linkedin.com/jobs/view/"):
        print(f"processing linkedin")
        scraper = LinkedInScraper(url)
        return scraper.parse()
    elif "myworkdayjobs.com" in url:
        print(f"processing workday")
        scraper = WorkdayScraper(url)
        return scraper.parse()

    else:
        return "other job website"
    return


def job_picker(job_data, jobs_to_filter, jobs_user_wants):
    for job in jobs_to_filter:
        if job.lower() in job_data['title'].lower():
            return False
    sys_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                 prompt_name='sys_initial_job_filter.txt')
    user_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                  prompt_name='user_initial_job_filter.txt',
                                                  jinja2_placeholders={
                                                      'job_title': job_data['title'].lower(),
                                                      'job_preferences': jobs_user_wants,
                                                      'job_filters': jobs_to_filter
                                                  })
    response = get_model_response(system_prompt=sys_prompt,
                                  user_prompt=user_prompt)
    response_txt = response.choices[0].message.content
    if response_txt == "True":
        return True
    else:
        return False

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
            return latest_message
        else:
            return None

async def main():
    last_message_id = None

    while True:
        message = await poll_channel(1771924936)
        if message.id != last_message_id:
            last_message_id = message.id
            test_message = """
                🧑‍💼  |  Responsible AI Data Scientist

                Empresa: Latinx in AI (LXAI)
                Ubicación: Costa Rica (On-site)
                Tags: #data

                https://www.linkedin.com/jobs/view/4225833956
            """
            print("Last message:", message.message)
            # job_posting_data = message_regex(history.messages[0].message)
            job_posting_data = message_regex(test_message)
            chosen_job = job_picker(job_data=job_posting_data,
                                    jobs_to_filter=FILTER_JOBS_KEYWORDS,
                                    jobs_user_wants=JOB_TYPE_TARGETS)
            if chosen_job:
                data = scraper_classifier(job_posting_data)
                result = assess_user(data)
                print(result)
                generated_cv = generate_resume(data)
                save_results(job_title=job_posting_data['title'],
                             job_company=job_posting_data['company'],
                             resume=generated_cv)

            else:
                print("Job is not a good fit. ")

        await asyncio.sleep(10)

with client:
    client.loop.run_until_complete(main())

