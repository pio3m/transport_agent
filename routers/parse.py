from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import os
from typing import Any, Dict
from datetime import date
from utils.cargo_calculator import CargoCalculator
from schemas.structured_output import ParseRequest, ParseResponse
from agents.llm_agent import LLMAgent
from config import settings
from utils.date_utils import process_polish_date


router = APIRouter(
    prefix=settings.API_V1_STR,
    tags=["parse"],
    responses={404: {"description": "Not found"}},
)


def get_llm_agent() -> LLMAgent:
    """
    Dependency to get the LLM agent instance.
    
    Returns:
        LLMAgent: An instance of the LLM agent
    """
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="LLM_API_KEY environment variable is not set"
        )
    return LLMAgent(api_key=api_key)


@router.post("/parse", response_model=ParseResponse)
async def parse_transport_request(
    request: ParseRequest,
    llm_agent: LLMAgent = Depends(get_llm_agent),
) -> Dict[str, Any]:
    try:
        # Przetwórz prompt przez LLM
        parsed_data = llm_agent.parse_transport_request(request.prompt, system_prompt_path="prompts/p_v1.txt")

       # Przetwarzanie dat względnych na konkretne daty
        for date_field in ["pickup_date", "delivery_date"]:
            if date_field in parsed_data and isinstance(parsed_data[date_field], str):
                parsed_data[date_field] = process_polish_date(parsed_data[date_field])


        # Oblicz LDM i analizę ładunku
        vehicle_type = parsed_data.get("vehicle_type", "brak")
        cargo_items = parsed_data.get("cargo_items", [])

        if vehicle_type == "brak":
            # domyślnie naczepa – może też być logika "dowolny"
            vehicle_type = "naczepa"

        calculator = CargoCalculator(vehicle_type=vehicle_type)
        cargo_result = calculator.calculate(cargo_items)

        # Rozszerz dane wyjściowe
        parsed_data["cargo_analysis"] = cargo_result

        # Wyznacz optymalny pojazd
        suggestion = CargoCalculator.suggest_optimal_vehicle(cargo_items)
        parsed_data["vehicle_suggestion"] = suggestion["vehicle"]


        # Zbuduj odpowiedź
        response = {
            "parsed_data": parsed_data,
            "raw_prompt": request.prompt
        }

        return response

    except Exception as e:
        print(f"Error parsing transport request: {str(e)}")
        default_response = {
            "parsed_data": {
                "vehicle_type": "brak",
                "cargo_items": [],
                "pickup_postal_code": None,
                "delivery_postal_code": None,
                "pickup_date": None,
                "delivery_date": None,
                "is_urgent": False,
                "is_stackable": False,
                "cargo_analysis": {
                    "ldm": 0,
                    "fit_in_vehicle": False,
                    "warnings": ["Błąd podczas przetwarzania"],
                    "total_weight": 0
                }
            },
            "raw_prompt": request.prompt
        }
        return default_response
