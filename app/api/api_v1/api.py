from fastapi import APIRouter

from app.api.api_v1.endpoints import apartment_price


api_router = APIRouter()
api_router.include_router(apartment_price.router, prefix="/apartment-price", tags=["apartment-price"])
