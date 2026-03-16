# backend/create_tables.py

import asyncio
from app.database import engine  # импортируем движок из database.py
from app import models  # импортируем модели, чтобы они зарегистрировались в Base

async def init_db():
    # Создаём все таблицы, описанные в моделях
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
    print("Таблицы успешно созданы!")