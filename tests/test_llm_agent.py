import pytest
from datetime import date, datetime, timedelta
from agents.llm_agent import LLMAgent

@pytest.fixture
def llm_agent():
    return LLMAgent(api_key="dummy_key")

def test_process_dates_with_iso_format(llm_agent):
    data = {
        "pickup_date": "2024-03-20",
        "delivery_date": "2024-03-21"
    }
    llm_agent._process_dates(data)
    assert data["pickup_date"] == "2024-03-20"
    assert data["delivery_date"] == "2024-03-21"

def test_process_dates_with_relative_dates(llm_agent):
    today = datetime.now().date()
    data = {
        "pickup_date": "jutro",
        "delivery_date": "za 3 dni"
    }
    llm_agent._process_dates(data)
    assert data["pickup_date"] == (today + timedelta(days=1)).isoformat()
    assert data["delivery_date"] == (today + timedelta(days=3)).isoformat()

def test_process_dates_with_mixed_formats(llm_agent):
    today = datetime.now().date()
    data = {
        "pickup_date": "2024-03-20",
        "delivery_date": "pojutrze"
    }
    llm_agent._process_dates(data)
    assert data["pickup_date"] == "2024-03-20"
    assert data["delivery_date"] == (today + timedelta(days=2)).isoformat()

def test_process_dates_with_empty_dates(llm_agent):
    data = {
        "pickup_date": "",
        "delivery_date": None
    }
    llm_agent._process_dates(data)
    assert data["pickup_date"] == ""
    assert data["delivery_date"] is None

def test_process_dates_with_invalid_format(llm_agent):
    data = {
        "pickup_date": "invalid-date",
        "delivery_date": "za X dni"
    }
    llm_agent._process_dates(data)
    assert data["pickup_date"] == "invalid-date"
    assert data["delivery_date"] == "za X dni" 