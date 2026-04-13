# backend/app/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas
from .auth import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str):
    """
    Получает пользователя по email.
    Возвращает объект User или None, если пользователь не найден.
    """
    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    """
    Создаёт нового пользователя.
    Принимает схему UserCreate, хеширует пароль и сохраняет в БД.
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()          # сохраняем изменения
    await db.refresh(db_user)   # обновляем объект (чтобы получить id и created_at)
    return db_user

async def create_link(
    db: AsyncSession,
    link: schemas.LinkCreate,
    user_id: int,
    short_code: str
):
    """
    Создаёт короткую ссылку для пользователя.
    Принимает оригинальный URL, id пользователя и сгенерированный короткий код.
    """
    db_link = models.Link(
        original_url=link.original_url,
        short_code=short_code,
        user_id=user_id
    )
    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    return db_link

async def get_user_links(db: AsyncSession, user_id: int):
    """
    Возвращает все ссылки, принадлежащие пользователю.
    """
    result = await db.execute(
        select(models.Link).where(models.Link.user_id == user_id)
    )
    return result.scalars().all()

async def get_link_by_code(db: AsyncSession, short_code: str):
    """
    Находит ссылку по короткому коду.
    Используется при редиректе.
    """
    result = await db.execute(
        select(models.Link).where(models.Link.short_code == short_code)
    )
    return result.scalar_one_or_none()

async def increment_clicks(db: AsyncSession, link: models.Link):
    """
    Увеличивает счётчик кликов для ссылки.
    """
    link.clicks += 1
    await db.commit()
    # Не делаем refresh, так как обновляем только одно поле

async def delete_link(db: AsyncSession, link: models.Link):
    #Удаляет ссылку из базы данных
    await db.delete(link)
    await db.commit()