import os
import json
import requests
from typing import Dict, Any
from datetime import datetime

from config import settings 

class LLMAgent:
    def __init__(self, provider: str = None, model_name: str = None, api_key: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.model_name = model_name or (settings.OLLAMA_MODEL if self.provider == "ollama" else "gpt-3.5-turbo")
        self.api_key = api_key or settings.LLM_API_KEY

        if self.provider == "openai":
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        elif self.provider == "ollama":
            self.api_url = "http://localhost:11434/api/generate"
        else:
            raise ValueError(f"Nieznany provider LLM: {self.provider}")


    def parse_transport_request(self, prompt: str, system_prompt_path: str) -> Dict[str, Any]:
        system_message = generate_system_prompt(system_prompt_path)

        full_prompt = f"{system_message.strip()}\n\n{prompt.strip()}"

        try:
            if self.provider == "openai":
                messages = [
                    {"role": "system", "content": system_message.strip()},
                    {"role": "user", "content": prompt.strip()}
                ]
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.1
                }
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                parsed_data = json.loads(content)

            elif self.provider == "ollama":
                payload = {
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "temperature": 0.1,
                    "stream": False
                }
                response = requests.post(self.api_url, json=payload)
                response.raise_for_status()
                result = response.json()
                content = result.get("response", "").strip()
                parsed_data = json.loads(content)

            return parsed_data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Błąd zapytania HTTP: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Błąd dekodowania JSON z odpowiedzi: {str(e)}")


def generate_system_prompt(base_prompt_path: str) -> str:
        today_str = datetime.today().strftime("%Y-%m-%d")

        with open(base_prompt_path, 'r', encoding='utf-8') as f:
            base_prompt = f.read()

        return f"Dzisiaj jest {today_str}.\n\n{base_prompt.strip()}"