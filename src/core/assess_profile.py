
from src.core.unpack_settings import USER_DESCRIPTION, USER_SKILLS, USER_EXPERIENCE, USER_PROJECTS, USER_LANGUAGES
from src.core.prompt_manager import get_prompt_template_from_jinja2
from src.llms.openai import openai_chat_completion
import ast  # to use ast.literal_eval(), convert string into python dictionary


def assess_user(job_description):
    """
    Evaluates the user's profile in relation to the job posting requirements.
    :param job_description: (string) description of the job posting
        {
            "description" : ... ,
            "responsabilities" : ... ,
            "requirements" : ...
            # sometimes other categories
        }

    :return: (dict[str, str]) Dictioary containing user assessment results
        {
            "profile_fit": can be "strong", "medium", or "weak" ,
            "education_requirements_met" can be "strong", "medium", or "weak": ,
            "knowledge_requirements_met": can be "strong", "medium", or "weak",
            "years_of_experience_met": can be "strong", "medium", or "weak",
            "summary": small summary provided by the LLM
        }
    """
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

    response = openai_chat_completion(system_prompt=sys_prompt,
                                  user_prompt=user_prompt)
    response_txt = response.choices[0].message.content
    try:
        response_dict = ast.literal_eval(response_txt)
        return response_dict
    except:
        print(f"ast.literal_eval() failed. LLM might not have returned a dictionary")
        return response_txt