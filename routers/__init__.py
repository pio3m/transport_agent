from fastapi import APIRouter
from .parse import router as parse_router

api_router = APIRouter()
api_router.include_router(parse_router)
