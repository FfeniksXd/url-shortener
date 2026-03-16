# backend/app/models.py

# Импортируем нужные типы полей и функции из SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func  # для автоматического добавления времени создания
from sqlalchemy.orm import relationship  # для связей между таблицами
from .database import Base  # импортируем базовый класс из database.py

# Таблица пользователей
class User(Base):
    __tablename__ = "users"  # имя таблицы в базе данных

    # Колонки таблицы:
    id = Column(Integer, primary_key=True, index=True)  # первичный ключ
    email = Column(String, unique=True, index=True, nullable=False)  # email, уникальный, не может быть пустым
    hashed_password = Column(String, nullable=False)  # хеш пароля
    is_active = Column(Boolean, default=True)  # активен ли пользователь (по умолчанию True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # дата регистрации (автоматически проставляется базой)

    # Связь с таблицей ссылок: у одного пользователя может быть много ссылок
    links = relationship("Link", back_populates="owner")

# Таблица ссылок
class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)  # длинный URL
    short_code = Column(String, unique=True, index=True, nullable=False)  # короткий код (уникальный)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # внешний ключ на пользователя
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # дата создания
    clicks = Column(Integer, default=0)  # счётчик переходов (по умолчанию 0)

    # Связь с пользователем
    owner = relationship("User", back_populates="links")