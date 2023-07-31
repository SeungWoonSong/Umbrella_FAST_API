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
        orm_mode = True

class UmbrellaBase(BaseModel):
    status: str
    location: Optional[str] = None

class UmbrellaCreate(UmbrellaBase):
    pass

class Umbrella(UmbrellaBase):
    id: int
    owner_id: Optional[int]

    class Config:
        orm_mode = True

class UmbrellaHistoryBase(BaseModel):
    umbrella_id: int
    user_id: int
    borrowed_at: datetime

class UmbrellaHistoryCreate(UmbrellaHistoryBase):
    pass

class UmbrellaHistory(UmbrellaHistoryBase):
    id: int
    returned_at: Optional[datetime]

    class Config:
        orm_mode = True

class BorrowUmbrella(BaseModel):
    user_id: int
    umbrella_id: int

class ReturnUmbrella(BaseModel):
    user_id: int
    umbrella_id: int

class UserWithUmbrella(BaseModel):
    user: User
    umbrella: Optional[Umbrella]
    status: str

    class Config:
        orm_mode = True
