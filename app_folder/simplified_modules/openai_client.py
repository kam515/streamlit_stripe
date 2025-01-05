import openai
from openai import OpenAI

def get_openai_client(api_key: str) -> OpenAI:
    """
    Returns an OpenAI client object using the provided API key.
    """
    return OpenAI(api_key=api_key)
