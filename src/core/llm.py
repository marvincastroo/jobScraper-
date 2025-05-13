from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
def get_model_response(system_prompt, user_prompt, model = "gpt-4.1-nano"):

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
    print(f"****LLM was called")
    return completion
