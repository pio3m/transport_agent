import os
import secrets
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "Transport Pricing API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    OLLAMA_MODEL: str = 'mistral'
    LLM_PROVIDER: str ='openai'
    # LLM_PROVIDER: str ='ollama'

    # API Keys
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    DISTANCE_API_KEY: str = os.getenv("DISTANCE_API_KEY", "")
    API_KEY: str = os.getenv("API_KEY", secrets.token_urlsafe(32))  # Generuje klucz jeśli nie istnieje

    # Langfuse Configuration
    LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    LANGFUSE_ENABLED: bool = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"

    # # Vehicles
    # VEHICLE_TYPES = {
    #     "bus": {
    #         "max_length": 420,  # cm
    #         "max_width": 220,   # cm
    #         "max_height": 220,  # cm
    #         "max_weight": 1500, # kg
    #         "ldm_capacity": 7,  # loading meters
    #     },
    #     "solowka": {
    #         "max_length": 720,  # cm
    #         "max_width": 245,   # cm
    #         "max_height": 270,  # cm
    #         "max_weight": 12000, # kg
    #         "ldm_capacity": 15,  # loading meters
    #     },
    #     "naczepa": {
    #         "max_length": 1360, # cm
    #         "max_width": 245,   # cm
    #         "max_height": 270,  # cm
    #         "max_weight": 24000, # kg
    #         "ldm_capacity": 33,  # loading meters
    #     },
    # }

settings = Settings()

# Wyświetl wygenerowany klucz API przy starcie
print(f"Twój klucz API: {settings.API_KEY}")