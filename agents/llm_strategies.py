from abc import ABC, abstractmethod
import json
import requests
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='llm_responses.log'
)
logger = logging.getLogger('llm_strategies')

class LLMStrategy(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_message: str, model_name: str) -> Dict[str, Any]:
        pass

    def _log_response(self, provider: str, raw_response: str):
        logger.info(f"Provider: {provider}\nRaw Response:\n{raw_response}\n{'='*50}")

class OpenAIStrategy(LLMStrategy):
    def __init__(self, api_key: str):
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def generate_response(self, prompt: str, system_message: str, model_name: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system_message.strip()},
            {"role": "user", "content": prompt.strip()}
        ]
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.1
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        self._log_response("OpenAI", content)
        return json.loads(content)

class OllamaStrategy(LLMStrategy):
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"

    def generate_response(self, prompt: str, system_message: str, model_name: str) -> Dict[str, Any]:
        full_prompt = f"{system_message.strip()}\n\n{prompt.strip()}"
        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "temperature": 0.1,
            "stream": False
        }
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result.get("response", "").strip()
        self._log_response("Ollama", content)
        return json.loads(content) 