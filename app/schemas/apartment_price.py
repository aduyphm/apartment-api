from typing import Optional, List
from fastapi import Query
from pydantic import BaseModel


class ApartmentPriceInput(BaseModel):
    province_code: str = Query(min_length=1, max_length=200, regex="^[0-9]*$")
    district_code: str = Query(min_length=1, max_length=200, regex="^[0-9]*$")
    ward_code: str = Query(min_length=1, max_length=200, regex="^[0-9]*$")
    street: Optional[str] = Query(default=None, min_length=0, max_length=2000)
    project_name: Optional[str] = Query(default=None, min_length=0, max_length=2000)
    apartment_name: Optional[str] = Query(default=None, min_length=0, max_length=1000)
    n_bedrooms: Optional[int] = Query(default=None, ge=0, le=1000)
    area: float = Query(ge=25, le=300)


class ApartmentPriceOutput(BaseModel):
    result: int
    price: float
    price_range: List[float] = []
