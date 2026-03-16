# backend/app/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ---------- Схемы для пользователей ----------
class UserBase(BaseModel):
    email: EmailStr  # автоматически проверяет, что это валидный email

class UserCreate(UserBase):
    password: str  # пароль при регистрации

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # позволяет работать с SQLAlchemy моделями

# ---------- Схемы для токенов (JWT) ----------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None  # может быть пустым, если токен невалиден

# ---------- Схемы для ссылок ----------
class LinkBase(BaseModel):
    original_url: str

class LinkCreate(LinkBase):
    pass  # пока ничего дополнительного не нужно

class LinkOut(LinkBase):
    id: int
    short_code: str
    clicks: int
    created_at: datetime

    class Config:
        from_attributes = True