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
from utils.distance_tool import get_distance_osm

router = APIRouter(
    prefix=settings.API_V1_STR,
    tags=["parse"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=Dict[str, str])
def health_check() -> Dict[str, str]:
    """
    Endpoint to check the health of the API.
    
    Returns:
        Dict[str, str]: A simple health check response
    """
    return {"status": "ok", "version": settings.VERSION}


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

        # obliczanie dystansu
        origin = parsed_data.get("pickup_postal_code")
        dest = parsed_data.get("delivery_postal_code")

        if origin and dest:
            parsed_data["distance_km"] = round(get_distance_osm(origin, dest), 1)
            
       # Przetwarzanie dat względnych na konkretne daty
        for date_field in ["pickup_date", "delivery_date"]:
            if date_field in parsed_data and isinstance(parsed_data[date_field], str):
                parsed_data[date_field] = process_polish_date(parsed_data[date_field])


        # Oblicz LDM i analizę ładunku
        vehicle_type = parsed_data.get("vehicle_type", "brak")
        cargo_items = parsed_data.get("cargo_items", [])

        calculate_cargo(parsed_data, vehicle_type, cargo_items)

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
                    "warnings": ["Błąd podczas przetwarzania" + str(e)],
                    "total_weight": 0
                }
            },
            "raw_prompt": request.prompt
        }
        return default_response

def calculate_cargo(parsed_data, vehicle_type, cargo_items):
    print(parsed_data)

    if vehicle_type == "brak":
        vehicle_type = "naczepa"
   
    calculator = CargoCalculator(vehicle_type=vehicle_type)

     # Spr czy są dane o ładunku - jesli nie to dajemy max ldm dla danego pojazdu
    if not cargo_items:
        parsed_data["cargo_analysis"] = {
               "ldm": calculator.get_max_ldm(),
                "fit_in_vehicle": True,
                "warnings": ["Brak danych o ładunku. Zwracamy maksymalny LDM dla podanego pojazdu."],
                "vehicle_used": vehicle_type,
                "vehicle_suggestion": 'brak',
                "total_weight": 0,
        }
        return
    
    # Oblicz LDM i analizę ładunku
    cargo_result = calculator.calculateLDM(cargo_items)

    if calculator.check_ldm(cargo_result["ldm"]):
        cargo_result["fit_in_vehicle"] = False
        cargo_result["warnings"].append(f"Ładunek przekracza maksymalną dopuszczalną ładowność dla pojazdu {vehicle_type}.")

    # Rozszerz dane wyjściowe
    parsed_data["cargo_analysis"] = cargo_result




        # Wyznacz optymalny pojazd
        # TODO do poprawy
    suggestion = CargoCalculator.suggest_optimal_vehicle(cargo_items)
    parsed_data["vehicle_suggestion"] = suggestion["vehicle"]
