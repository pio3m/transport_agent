from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import date
from enum import Enum


class VehicleType(str, Enum):
    BUS = "bus"
    SOLO = "solówka"
    TRAILER = "naczepa"
    NONE = "brak"


class CargoItem(BaseModel):
    width: Optional[float] = Field(None, description="Szerokość ładunku w metrach")
    length: Optional[float] = Field(None, description="Długość ładunku w metrach")
    height: Optional[float] = Field(None, description="Wysokość ładunku w metrach")
    quantity: Optional[int] = Field(None, description="Ilość sztuk ładunku")
    total_weight: Optional[float] = Field(None, description="Waga jednego ładunku w kilogramach")


class CargoAnalysis(BaseModel):
    ldm: Optional[float] = None
    fit_in_vehicle: Optional[bool] = None
    warnings: Optional[List[str]] = None
    total_weight: Optional[int] = None
    vehicle_used: Optional[str] = None
    vehicle_suggestion: Optional[str] = Field(default=None, description="Sugerowany typ pojazdu")


class TransportRequest(BaseModel):
    cargo_items: List[CargoItem] = Field(..., description="Lista ładunków")
    pickup_postal_code: Optional[str] = Field(None, description="Kod pocztowy miejsca odbioru")
    delivery_postal_code: Optional[str] = Field(None, description="Kod pocztowy miejsca dostawy")
    pickup_date: Optional[Union[date, str]] = Field(default=None, description="Data odbioru")
    delivery_date: Optional[Union[date, str]] = Field(default=None, description="Data dostawy")
    is_urgent: bool = Field(False, description="Czy zlecenie jest pilne")
    is_stackable: bool = Field(False, description="Czy ładunki można piętrować")
    cargo_analysis: Optional[CargoAnalysis] = None
    distance_km: Optional[float] = None



class ParseRequest(BaseModel):
    prompt: str = Field(..., description="Tekst zlecenia transportowego do analizy")


class ParseResponse(BaseModel):
    parsed_data: TransportRequest = Field(..., description="Ustrukturyzowane dane wyekstrahowane z prompta")
    raw_prompt: str = Field(..., description="Oryginalny prompt tekstowy")