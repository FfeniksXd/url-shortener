# backend/app/schemas.py

from pydantic import BaseModel, EmailStr, field_validator
import re
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
    custom_code: str | None = None

    @field_validator('custom_code')
    def validate_custom_code(cls, v):
        # Если код не передан – пропускаем (сгенерируется случайный)
        if v is None:
            return v

        # 1. Проверка длины
        if not (3 <= len(v) <= 30):
            raise ValueError('Custom code must be between 3 and 30 characters long')

        # 2. Проверка разрешённых символов
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Custom code may only contain letters, numbers, hyphen and underscore')

        # 3. Не начинается и не заканчивается на - или _
        if v[0] in '-_' or v[-1] in '-_':
            raise ValueError('Custom code cannot start or end with hyphen or underscore')

        return v

class LinkOut(LinkBase):
    id: int
    short_code: str
    clicks: int
    created_at: datetime

    class Config:
        from_attributes = True

class LinkUpdate(BaseModel):
    original_url: str