import os
from openai import OpenAI

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
NEMOTRON_MODEL = "nvidia/nemotron-3-super-120b-a12b"


class NIMClient:
    def __init__(self, api_key: str = None):
        key = api_key or os.environ.get("NIM_API_KEY")
        if not key:
            raise ValueError("NIM_API_KEY not set. Get a free key at https://build.nvidia.com")
        self._client = OpenAI(base_url=NIM_BASE_URL, api_key=key)

    def chat(self, messages: list[dict], temperature: float = 0.2, max_tokens: int = 2048,
             model: str = NEMOTRON_MODEL) -> str:
        response = self._client.chat.completions.create(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens
        )
        return response.choices[0].message.content
