from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum


class VehicleType(str, Enum):
    BUS = "bus"
    SOLO = "solówka"
    TRAILER = "naczepa"
    NONE = "brak"


class CargoItem(BaseModel):
    width: float = Field(..., description="Szerokość ładunku w metrach")
    length: float = Field(..., description="Długość ładunku w metrach")
    height: float = Field(..., description="Wysokość ładunku w metrach")
    quantity: int = Field(..., description="Ilość sztuk ładunku")


class TransportRequest(BaseModel):
    vehicle_type: VehicleType = Field(..., description="Typ pojazdu")
    cargo_items: List[CargoItem] = Field(..., description="Lista ładunków")
    pickup_postal_code: Optional[str] = Field(None, description="Kod pocztowy miejsca odbioru")
    delivery_postal_code: Optional[str] = Field(None, description="Kod pocztowy miejsca dostawy")
    pickup_date: Optional[date] = Field(None, description="Data odbioru")
    delivery_date: Optional[date] = Field(None, description="Data dostawy")
    is_urgent: bool = Field(False, description="Czy zlecenie jest pilne")
    is_stackable: bool = Field(False, description="Czy ładunki można piętrować")


class ParseRequest(BaseModel):
    prompt: str = Field(..., description="Tekst zlecenia transportowego do analizy")


class ParseResponse(BaseModel):
    parsed_data: TransportRequest = Field(..., description="Ustrukturyzowane dane wyekstrahowane z prompta")
    raw_prompt: str = Field(..., description="Oryginalny prompt tekstowy")