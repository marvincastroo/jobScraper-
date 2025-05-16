from dotenv import load_dotenv
import os
import asyncio
import re

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel

from src.llms.openai import openai_chat_completion
from src.core.prompt_manager import get_prompt_template_from_jinja2

from src.scrapers.scrapper_classifier import scraper_classifier
from src.core.assess_profile import assess_user
from src.core.generate_resume import generate_resume
from src.core.save_results import save_results
from src.core.sendTelegramMessage import sendTelegramMessage
from src.core.unpack_settings import (FILTER_JOBS_KEYWORDS, JOB_TYPE_TARGETS, FILTER_COMPANIES, JOB_FINDINGS_FILTER,
                                      USER_DESCRIPTION)
# from settings import FILTER_JOBS_KEYWORDS, JOB_TYPE_TARGETS, FILTER_COMPANIES, JOB_FINDINGS_FILTER, USER_DESCRIPTION

load_dotenv()

TELEGRAM_API_ID = int(os.getenv('app_api_id'))
TELEGRAM_API_HASH = os.getenv('app_api_hash')

client = TelegramClient("test", TELEGRAM_API_ID, TELEGRAM_API_HASH)


def check_job_in_results(job_data):
    """
    Checks if the current job is a duplicate or has already been stored in output/. If that's the case, current job
    is not processed.
    :param job_data : (dict[str, str]) dictionary with the job posting's info. Contains at least
        {
            'title' : string,
            'company' : string,
            'link': string
        }
    :return: (bool)
    """
    job_title = job_data['title']
    job_company = job_data['company']
    directory_name = (job_title + job_company).lower()
    directory_name = directory_name.replace(" ", "_")
    directory_name = re.sub(r'[^a-z0-9_\-]', '', directory_name)
    if os.path.exists("../../output/" + directory_name):
        print(f"Job posting already exists in results folder output/{directory_name}")
        return True
    else:
        return False


def job_picker(job_data, jobs_to_filter, jobs_user_wants, companies_to_filter):
    """
    Initial filter of jobs based on the posting's main information and the user's preferences.
    First, checks if the job title has a banned keyword (contents of jobs_to_filter). If it has one, it's instantly
    rejected.
    Then, it checks if the job title has a preferred keyword (contents of job_users_wants). If it has one, it's
    instantly approved.
    Afterward, checks if the company's name is banned (contents of companies_to_filter). If it is, the job is
    instantly rejected.
    If the job hasn't been approved or rejected by then, it is input into the LLM for it to decide, based on the
    settings.py variable USER_DESCRIPTION

    :param job_data: (dict[str, str]) dictionary with the job posting's info. Contains at least
        {
            'title' : string,
            'company' : string,
            'link': string
        }
    :param jobs_to_filter: list[str], keywords that will trigger a rejection if at least one is contained in the
    job's title.
    :param jobs_user_wants: list[str], keywords that will trigger an approval if at least one is contained in the
    job's title.
    :param companies_to_filter: list[str], list of companies that will trigger a rejection.
    :return: (bool)
    """
    for unwanted_job in jobs_to_filter:
        if unwanted_job.lower() in job_data['title'].lower():
            return False
    for wanted_job in jobs_user_wants:
        if wanted_job.lower() in job_data['title'].lower():
            return True
    for company in companies_to_filter:
        if company.lower() in job_data['company'].lower():
            return False

    sys_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                 prompt_name='sys_initial_job_filter.txt')
    user_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                  prompt_name='user_initial_job_filter.txt',
                                                  jinja2_placeholders={
                                                      'job_title': job_data['title'],
                                                      'user_description': USER_DESCRIPTION,
                                                      'job_preferences': jobs_user_wants,
                                                      'job_filters': jobs_to_filter
                                                  })
    print(sys_prompt + user_prompt) # TODO: remove
    response = openai_chat_completion(system_prompt=sys_prompt,
                                  user_prompt=user_prompt)
    response_txt = response.choices[0].message.content
    print(response_txt)
    # LLM will output only 'True' if the job is a good fit.
    if response_txt == "True":
        return True
    else:

        return False


def message_regex(message):
    """
    Parses the telegram message to obtain the relevant job information, like the job's title, company, link, etc.
    :param message: (str), String to be analized.
    :return: (dict[str, str])
    """
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

    # for key, value in result.items():
    #     if value:
    #         print(f"{key.capitalize()}: {value}")

    return result


async def poll_channel(channel_id):
    """
    Reads the latest message sent to the chat
    :param channel_id: (int) ID of the chat to be monitored
    :return: (telethon.Messages.message)
    """
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


async def process_message(message):
    """
    1. Checks if the job has already been processed before to handle duplicates or identical jobs, in order to
        reduce API costs. If it has been processed, it's dumped.
    2. Check if the job is within the user's interests ( job_picker() ) if not, dumped.
    3. Calls scraper_classifier() to get detailed info on the job: description, requirements, etc.
    4. Assess the user's profile with the info obtained in step #3.
    5. If user's fit is good enough (profile fit result is inside JOB_FINDINGS_FILTER), the resume will be generated
        on output/{job_title}{company}
    6. Sends the alert in Telegram
    :param message: (string), string of the last message in the chat
    :return:
    """
    job_posting_data = message_regex(message)
    entry_already_exists = check_job_in_results(job_posting_data)
    if entry_already_exists:
        return "job was already processed | found in output/"

    chosen_job = job_picker(job_data=job_posting_data,
                            jobs_to_filter=FILTER_JOBS_KEYWORDS,
                            jobs_user_wants=JOB_TYPE_TARGETS,
                            companies_to_filter=FILTER_COMPANIES)

    # if not chosen_job:
    #     return "Job is not a good fit"
    #
    # data = scraper_classifier(job_posting_data)
    # if data is None:
    #     return "That website doesn't have a designated scrapper - Can't access the job's basic info. Skipping job"
    #
    # """
    # Checks if the profile_fit result is inside JOB_FINDINGS_FILTER. profile_fit can be either 'strong', 'medium', or
    # 'weak'. Acceptable results are contained in JOB_FINDINGS_FILTER.
    # """
    # user_assessment_result = assess_user(data)
    # if user_assessment_result['profile_fit'].lower() not in JOB_FINDINGS_FILTER:
    #     return "Profile fit doesn't meet required criteria stated in JOB_FINDINGS_FILTER (settings.py)"
    #
    # generated_cv = generate_resume(data)
    # save_results(job_title=job_posting_data['title'],
    #              job_company=job_posting_data['company'],
    #              resume=generated_cv,
    #              user_assessment=user_assessment_result)
    #
    # await sendTelegramMessage(initial_job_info=job_posting_data)
    return True


async def main():
    """
    Polls the telegram channel's last message every 10 seconds. Checks if the message is different from the one before,
    if it is, calls process_message().
.
    """
    last_message_id = None

    while True:
        message = await poll_channel(1771924936)
        if message.id != last_message_id:
            last_message_id = message.id
            test_message = """
            🧑‍💼  |  Electrical Planning I
            
            Empresa: Recruiter
            Ubicación: Heredia, Heredia, Costa Rica (Hybrid)
            Tags: #soporte
            
            https://www.linkedin.com/jobs/view/4228542522
            """
            # print("Last message:", message.message)
            print("Last message:", test_message)
            # job_posting_data = message_regex(message.message)
            # success = await process_message(message.message)
            success = await process_message(test_message)
            if success != True:
                print(success)

        await asyncio.sleep(10)

with client:
    client.loop.run_until_complete(main())
