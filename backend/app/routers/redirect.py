# backend/app/routers/redirect.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .. import crud
from ..database import get_db

router = APIRouter(tags=["redirect"])

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Перенаправляет с короткой ссылки на оригинальный URL.
    Увеличивает счётчик кликов.
    """
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Увеличиваем счётчик кликов
    await crud.increment_clicks(db, link)
    
    # Возвращаем редирект (302 - временный)
    return RedirectResponse(url=link.original_url, status_code=302)