import pytest
from unittest.mock import Mock, patch
import requests
import json
from agents.llm_agent import LLMAgent
from agents.llm_strategies import OpenAIStrategy, OllamaStrategy

@pytest.fixture
def llm_agent():
    return LLMAgent(provider="openai", api_key="dummy_key")

def test_parse_transport_request_success(llm_agent):
    mock_response = {
        "vehicle_type": "bus",
        "cargo_items": [{
            "width": 1.0,
            "length": 2.0,
            "height": 1.5,
            "quantity": 2
        }],
        "pickup_postal_code": "00-001",
        "delivery_postal_code": "00-002",
        "pickup_date": "2024-03-20",
        "delivery_date": "2024-03-21",
        "is_urgent": False
    }
    
    with patch.object(llm_agent.strategy, 'generate_response', return_value=mock_response):
        result = llm_agent.parse_transport_request(
            prompt="Test prompt",
            system_prompt_path="prompts/p_v1.txt"
        )
        assert result == mock_response

def test_parse_transport_request_http_error(llm_agent):
    with patch.object(llm_agent.strategy, 'generate_response', side_effect=requests.exceptions.RequestException("HTTP Error")):
        with pytest.raises(Exception) as exc_info:
            llm_agent.parse_transport_request(
                prompt="Test prompt",
                system_prompt_path="prompts/p_v1.txt"
            )
        assert "Błąd zapytania HTTP" in str(exc_info.value)

def test_parse_transport_request_json_error(llm_agent):
    with patch.object(llm_agent.strategy, 'generate_response', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
        with pytest.raises(Exception) as exc_info:
            llm_agent.parse_transport_request(
                prompt="Test prompt",
                system_prompt_path="prompts/p_v1.txt"
            )
        assert "Błąd dekodowania JSON" in str(exc_info.value)

def test_llm_agent_invalid_provider():
    with pytest.raises(ValueError) as exc_info:
        LLMAgent(provider="invalid_provider")
    assert "Nieznany provider LLM" in str(exc_info.value)

def test_llm_agent_default_provider():
    with patch('agents.llm_agent.settings.LLM_PROVIDER', 'openai'):
        agent = LLMAgent()
        assert agent.provider == 'openai'
        assert isinstance(agent.strategy, OpenAIStrategy)

def test_llm_agent_ollama_provider():
    agent = LLMAgent(provider="ollama")
    assert agent.provider == 'ollama'
    assert isinstance(agent.strategy, OllamaStrategy) 