# backend/app/routers/links.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, crud, auth
from ..database import get_db
import random
import string

router = APIRouter(prefix="/links", tags=["links"])

def generate_short_code(length: int = 6) -> str:
    """Генерирует случайный код из букв и цифр"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))



@router.post("/", response_model=schemas.LinkOut)
async def create_link(
    link: schemas.LinkCreate,
    current_user: schemas.UserOut = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Определяем, какой короткий код использовать
    if link.custom_code:
        short_code = link.custom_code
        # Проверяем, не занят ли этот код
        existing = await crud.get_link_by_code(db, short_code)
        if existing:
            raise HTTPException(status_code=400, detail="This short code is already taken")
    else:
        # 2. Если пользователь не задал код, генерируем случайный
        short_code = generate_short_code()
        existing = await crud.get_link_by_code(db, short_code)
        while existing:
            short_code = generate_short_code()
            existing = await crud.get_link_by_code(db, short_code)

    # 3. Создаём ссылку в базе данных
    return await crud.create_link(db, link, current_user.id, short_code)

@router.get("/", response_model=list[schemas.LinkOut])
async def read_my_links(
    current_user: schemas.UserOut = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает список всех ссылок текущего пользователя.
    """
    return await crud.get_user_links(db, current_user.id)


#находим нужную нам ссылку через короткий код
@router.delete("/{short_code}")
async def delete_link(
    short_code: str,
    current_user: schemas.UserOut = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    link = await crud.get_link_by_code(db, short_code)

    print(f"Received DELETE request for short_code: {short_code}") #временно

    if not link:
        raise HTTPException(status_code=404,detail="link not found")
    
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this link")
    await db.delete(link); await db.commit()

    return {"message": "Link deleted successfully"}


@router.put("/{short_code}", response_model=schemas.LinkOut)
async def update_link(
    short_code: str,
    link_update: schemas.LinkUpdate,   
    current_user: schemas.UserOut = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Находим ссылку
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # 2. Проверяем права
    if link.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to edit this link")
    
    # 3. Обновляем оригинальный URL
    link.original_url = link_update.original_url
    await db.commit()
    await db.refresh(link)
    
    return link

