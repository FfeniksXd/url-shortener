# backend/app/database.py

# Импортируем необходимые компоненты из SQLAlchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Строка подключения к базе данных PostgreSQL.
# Формат: postgresql+asyncpg://пользователь:пароль@хост/имя_базы
# Замени 'postgres', 'password' и 'urlshortener' на свои данные.
DATABASE_URL = "postgresql+asyncpg://postgres:7ujm7UJM@localhost/urlshortener"

# Создаём асинхронный движок SQLAlchemy.
# engine будет управлять подключениями к БД.
# echo=True включает логирование SQL-запросов (полезно для отладки).
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаём фабрику сессий.
# AsyncSessionLocal будет использоваться для получения сессий в каждом запросе.
# expire_on_commit=False означает, что объекты не будут автоматически "устаревать" после коммита.
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для моделей данных.
# Все наши таблицы будут наследоваться от этого класса.
Base = declarative_base()



async def get_db():
    async with AsyncSessionLocal() as session:
        yield session