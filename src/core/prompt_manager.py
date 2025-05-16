import sys
from jinja2 import Environment, FileSystemLoader


def get_prompt_template_from_jinja2(
    prompt_path: str,
    prompt_name: str,
    jinja2_placeholders: dict[str, str]={},
    ) -> str:
    """
    Loads a .txt file as a jinja2 template.
    :param prompt_path: (str) route to prompt directories
    :param prompt_name: (str) name of the .txt prompt file, including extension
    :param jinja2_placeholders: (dict[str, _]) placeholder variables to be replaced in the prompt
    :return: (string) prompt
    """


    env = Environment(loader=FileSystemLoader(prompt_path, encoding='utf-8'))
    template = env.get_template(prompt_name)
    prompt_string = template.render(jinja2_placeholders)


    return prompt_string

if __name__ == '__main__':
    prompt = get_prompt_template_from_jinja2(
        prompt_path="../prompts",
        prompt_name="scrapper.txt",
        jinja2_placeholders={"user_name": "Alex"}
    )
    print(prompt)

# print(promptTest2)