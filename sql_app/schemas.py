from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class UmbrellaBase(BaseModel):
    status: str = "available"


class UmbrellaCreate(UmbrellaBase):
    pass


class Umbrella(UmbrellaBase):
    id: int
    owner_name: Optional[str] = None

    class Config:
        from_attributes = True


class UmbrellaHistoryBase(BaseModel):
    umbrella_id: int
    user_name: str
    borrowed_at: datetime


class UmbrellaHistoryCreate(UmbrellaHistoryBase):
    pass


class UmbrellaHistory(UmbrellaHistoryBase):
    id: int
    returned_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserWithUmbrella(BaseModel):
    user: User
    umbrella: Optional[Umbrella]
    status: str

    class Config:
        from_attributes = True


class BorrowReturnResponse(BaseModel):
    user_name: str
    umbrella_id: int


class WeatherCondition(BaseModel):
    rain_probability: float
    uv_index: float
    uv_index_category: str

    class Config:
        from_attributes = True
