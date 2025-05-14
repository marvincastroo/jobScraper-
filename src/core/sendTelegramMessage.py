import os
import requests
import re
import asyncio
import telegram
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_API = os.getenv('TELEGRAM_BOT_API')
CHAT_ID = 1061543567
#
# message = "hello from your telegram bot \U0001F7E9 )"
# url = f"https://api.telegram.org/bot{TELEGRAM_BOT_API}/sendMessage?chat_id={CHAT_ID}&text={message}"
#
# r = requests.get(url)
# print(r.json())

async def sendTelegramMessage(initial_job_info):

    bot = telegram.Bot(token=TELEGRAM_BOT_API)

    async def send_txt(message):
        try:
            await bot.send_message(chat_id=CHAT_ID,
                                   text=message,
                                   parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
                                   )
            print(f"Message sent to chat: '{message}'")
            return True
        except telegram.error.TelegramError as e:
            print(f"Telegram error sending message: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False
    async def send_pdf(pdf_path, caption):
        try:
            with open(pdf_path, 'rb') as pdf_file:
                await bot.send_document(
                    chat_id=CHAT_ID,
                    document=pdf_file,
                    filename=os.path.basename('resume.pdf'),
                    caption=caption
                )
                print(f"PDF '{'resume.pdf'}' sent to chat ")
                return True
        except FileNotFoundError:
            print(f"Error: PDF file '{pdf_path}' not found.")
            return False

        except telegram.error.TelegramError as e:
            print(f"Telegram error sending PDF: {e}")
            return False

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False



    comments, pdf, tex = get_results(initial_job_info)
    if comments is None:
        print(f"error: get results returns none")
        return None

    comments_styled = comments_style(comments)
    job_title = initial_job_info['title']
    company = initial_job_info['company']
    link = initial_job_info['link']

    message_string = f'*{job_title}*\n*Company:* {company}\n{link}\n'
    full_txt = message_string + '\n' + comments_styled
    escape_chars = ['_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for escapeChar in escape_chars:
        full_txt = full_txt.replace(escapeChar, f'\\{escapeChar}')

    message_sent = await send_txt(full_txt)
    if message_sent is False:
        print("error sending message")
    pdf_sent = await send_pdf(pdf, None)
    if pdf_sent is False:
        print("error sending pdf")

def comments_style(comments_string):

    string = comments_string.replace("profile_fit", "Profile fit")
    string = string.replace("education_requirements_met", "*Education Requirements*")
    string = string.replace("knowledge_requirements_met", "*Technical Requirements*")
    string = string.replace("years_of_experience_met", "*YoE Requirements*")
    string = string.replace("summary", "*Summary*")

    string = string.replace(': strong', ": \U0001F7E9 Strong")  # green square
    string = string.replace(': medium', ": \U0001F7E8 Medium")  # yellow square
    string = string.replace(': weak', ": \U0001F7E5 Weak")      # red square

    return string

def get_results(initial_job_info):
    job_title = initial_job_info['title']
    job_company = initial_job_info['company']
    job_slug = (job_title + job_company).lower()
    job_slug = job_slug.replace(" ", "_")
    job_slug = re.sub(r'[^a-z0-9_\-]', '', job_slug)
    directory_name = "../../output/" + job_slug
    if os.path.exists(directory_name):
        with open(directory_name + '/comments.txt', 'r', encoding='utf-8') as file:
            comments_file = file.read()
        pdf_file = directory_name + '/main.pdf'
        tex_file = directory_name + '/main.tex'
        return comments_file, pdf_file, tex_file
    else:
        return None


if __name__ == "__main__":
    job = {'title':'job_posting', 'company':'ashitionyx', 'link':'https://chatgpt.com/c/6823f840-3340-8000-95f5-b1ae43b95cb0'}
    asyncio.run(sendTelegramMessage(job))
