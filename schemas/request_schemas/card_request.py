from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CardRequest(BaseModel):
    title: str
    comment: str
    main_photo: str
    price: int

class CardDelete(BaseModel):
    id: int

class UserRegister(BaseModel):
    login: str
    password: str
    email: str
    token: str


class UserLogin(BaseModel):
    login: str
    password: str


class UserEdit(BaseModel):
    login: Optional[str]
    password: Optional[str]
    email: Optional[str]
    token: Optional[str]
