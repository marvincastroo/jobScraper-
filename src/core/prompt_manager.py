import sys
from jinja2 import Environment, FileSystemLoader


def get_prompt_template_from_jinja2(
    prompt_path: str,
    prompt_name: str,
    jinja2_placeholders: dict[str, str]={},
    ) -> str:
    """
    Carga un .txt como un template de Jinja2, y lo convierte en un LangChain PromptTemplate

    Args:a
        prompt_path (str): ruta al prompt
        prompt_name (str): nombre del prompt, incluyendo extensión
        partial_variables (dict): Diccionario de partial variables cargadas por LangChain
        jinja2_placeholders (dict): Diccionario de placeholders a ser reemplazados por Jinja2
        :rtype: object

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