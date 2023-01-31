from datetime import date
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.dialects.postgresql import UUID


class User(BaseModel):
    email: EmailStr
    password: str
    first_name: str = None
    last_name: str = None
    birth_date: date = None

    class Config:
        orm_mode = False


class Validation(BaseModel):
    id: int
    user_id: int
    pin_code: str
    url: str
    time_email_sent: date
