from pydantic import BaseModel, field_validator
from typing import Optional, Union
import pandas as pd


class Car(BaseModel):
    stock_id: str
    km: int
    price: float
    make: str
    model: str
    year: int
    version: Optional[str] = None
    bluetooth: Optional[str] = None
    largo: Optional[float] = None
    ancho: Optional[float] = None
    altura: Optional[float] = None
    car_play: Optional[str] = None

    @field_validator('stock_id', mode='before')
    @classmethod
    def validate_stock_id(cls, v):
        return str(v)

    @field_validator('car_play', 'bluetooth', 'version', mode='before')
    @classmethod
    def validate_optional_strings(cls, v):
        if pd.isna(v) or v == '' or str(v).lower() == 'nan':
            return None
        return str(v)

    @field_validator('largo', 'ancho', 'altura', mode='before')
    @classmethod
    def validate_optional_floats(cls, v):
        if pd.isna(v) or str(v).lower() == 'nan':
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None


class CarFilter(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    max_km: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None


class FinancingRequest(BaseModel):
    car_price: float
    down_payment: float
    years: int  # 3-6 years
    
    
class FinancingPlan(BaseModel):
    car_price: float
    down_payment: float
    loan_amount: float
    years: int
    monthly_payment: float
    total_payment: float
    total_interest: float
    interest_rate: float = 0.10