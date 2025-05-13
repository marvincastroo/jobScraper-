from settings import USER_DESCRIPTION, USER_SKILLS, USER_EXPERIENCE, USER_PROJECTS, USER_LANGUAGES
from src.core.prompt_manager import get_prompt_template_from_jinja2
from src.core.llm import get_model_response
import ast  # to use ast.literal_eval(), convert string into python dictionary


if USER_DESCRIPTION is None:
    raise ValueError("USER_DESCRIPTION variable is not initialized in settings.py. A basic user description is necessary"
                     "for the tool to work.")

if USER_SKILLS is None:
    USER_SKILLS = ""
if USER_EXPERIENCE is None:
    USER_EXPERIENCE = ""
if USER_PROJECTS is None:
    USER_PROJECTS = ""
if USER_LANGUAGES is None:
    USER_LANGUAGES = ""

def assess_user(job_description):
    sys_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                 prompt_name='sys_detailed_job_filter.txt')
    user_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                  prompt_name='user_detailed_job_filter.txt',
                                                  jinja2_placeholders={
                                                      'user_description': USER_DESCRIPTION,
                                                      'user_skills': USER_SKILLS,
                                                      'user_experience': USER_EXPERIENCE,
                                                      'user_projects': USER_PROJECTS,
                                                      'user_languages': USER_LANGUAGES,
                                                      'job_description' : job_description,
                                                  })
    response = get_model_response(system_prompt=sys_prompt,
                                  user_prompt=user_prompt)
    response_txt = response.choices[0].message.content
    try:
        response_dict = ast.literal_eval(response_txt)
        return response_dict
    except:
        print(f"ast.literal_eval() failed. LLM might not have returned a dictionary")
        return response_txt