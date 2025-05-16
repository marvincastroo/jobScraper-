from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
def openai_chat_completion(system_prompt, user_prompt, model = "gpt-4.1-mini"):

    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
            # todo: learn about chached input
        ]
    )
    # completion = None

    return completion


def num_tokens_from_string(string, encoding_name='o200k_base'):
    """
    Obtains the number of tokens given a string and the encoding for that model.
    :param string: (string) prompt to obtain number of tokens.
    :param encoding_name: (string) encoding type for the tokenization. gpt-4o uses 'o200k_base'
    :return: (int) number of text tokens
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens