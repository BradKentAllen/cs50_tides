# model_user.py

'''
modified from Server1 with User_Adit and User_MapHouse

'''

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ValidationError, EmailStr


class Base_User(BaseModel):
    user_ID: int
    email: EmailStr
    hash_password: bytes
    salt: bytes

    name: Optional[str] = None

    created_date: date = datetime.now()

    authority: str = 'general'  # authority level within this organization
    org: str = 'AditNW'

    last_login: date = datetime(1980, 1, 1)
    company: Optional[str]


class User_Adit(Base_User):
    process_authority: str = 'technician'
    qualified_process_list: Optional[List[str]]





