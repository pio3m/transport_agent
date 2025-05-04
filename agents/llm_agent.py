import json
import requests
from typing import Dict, Any
from datetime import datetime

from config import settings
from .llm_strategies import OpenAIStrategy, OllamaStrategy

class LLMAgent:
    def __init__(self, provider: str = None, model_name: str = None, api_key: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.model_name = model_name or (settings.OLLAMA_MODEL if self.provider == "ollama" else "gpt-3.5-turbo")
        self.api_key = api_key or settings.LLM_API_KEY

        if self.provider == "openai":
            self.strategy = OpenAIStrategy(self.api_key)
        elif self.provider == "ollama":
            self.strategy = OllamaStrategy()
        else:
            raise ValueError(f"Nieznany provider LLM: {self.provider}")

    def parse_transport_request(self, prompt: str, system_prompt_path: str) -> Dict[str, Any]:
        system_message = generate_system_prompt(system_prompt_path)

        try:
            return self.strategy.generate_response(prompt, system_message, self.model_name)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Błąd zapytania HTTP: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Błąd dekodowania JSON z odpowiedzi: {str(e)}")


def generate_system_prompt(base_prompt_path: str) -> str:
        today_str = datetime.today().strftime("%Y-%m-%d")

        with open(base_prompt_path, 'r', encoding='utf-8') as f:
            base_prompt = f.read()

        return f"Dzisiaj jest {today_str}.\n\n{base_prompt.strip()}"