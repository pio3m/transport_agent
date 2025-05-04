from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import os
from typing import Any, Dict

from schemas.structured_output import ParseRequest, ParseResponse, TransportRequest
from agents.llm_agent import LLMAgent
from config import settings
from security import get_api_key

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
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    """
    Parse a transport request text and extract structured data using OpenAI's GPT-4.
    
    Args:
        request (ParseRequest): The request containing the transport prompt
        llm_agent (LLMAgent): The LLM agent to use for parsing
        api_key (str): The API key for authentication
        
    Returns:
        Dict[str, Any]: The parsed data and original prompt
    """
    try:
        # Send prompt to LLM agent for parsing
        parsed_data = llm_agent.parse_transport_request(request.prompt)
        
        # Create response
        response = {
            "parsed_data": parsed_data,
            "raw_prompt": request.prompt
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing transport request: {str(e)}"
        )