# from settings import (USER_NAME, USER_EDUCATION, USER_SKILLS, USER_EXPERIENCE, USER_PROJECTS, USER_LANGUAGES,
#                       USER_CERTIFICATIONS)
from src.core.unpack_settings import (USER_NAME, USER_EDUCATION, USER_SKILLS, USER_EXPERIENCE, USER_PROJECTS, USER_LANGUAGES,
                                      USER_CERTIFICATIONS)
from src.core.prompt_manager import get_prompt_template_from_jinja2
from src.llms.openai import openai_chat_completion

def generate_resume(job_description):
    with open('../../latex_format.tex', 'r') as file:
        latex = file.read()

    sys_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                 prompt_name='sys_generate_resume.txt',
                                                 jinja2_placeholders={
                                                     "latex_format": latex
                                                 })
    user_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                  prompt_name='user_generate_resume.txt',
                                                  jinja2_placeholders={
                                                      'user_name': USER_NAME,
                                                      'user_education': USER_EDUCATION,
                                                      'user_experience': USER_EXPERIENCE,
                                                      'user_skills': USER_SKILLS,
                                                      'user_projects': USER_PROJECTS,
                                                      'user_languages': USER_LANGUAGES,
                                                      'user_certifications': USER_CERTIFICATIONS,
                                                      'job_description': job_description})

    response = openai_chat_completion(system_prompt=sys_prompt,
                                  user_prompt=user_prompt)
    response_txt = response.choices[0].message.content

    return response_txt

