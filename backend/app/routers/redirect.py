from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .. import crud
import time
from ..database import get_db, AsyncSessionLocal
import asyncio


def parse_user_agent_py(user_agent: str):
    ua = user_agent.lower()
    # Device
    if 'mobile' in ua or 'iphone' in ua or 'android' in ua:
        device = 'mobile'
    else:
        device = 'desktop'
    # OS
    if 'windows' in ua:
        os = 'Windows'
    elif 'mac' in ua:
        os = 'macOS'
    elif 'android' in ua:
        os = 'Android'
    elif 'linux' in ua:
        os = 'Linux'

    elif 'iphone' in ua or 'ipad' in ua:
        os = 'iOS'
    else:
        os = 'Unknown'
    # Browser
    if 'edg' in ua:
        browser = 'Edge'
    elif 'firefox' in ua:
        browser = 'Firefox'
    elif 'chrome' in ua:
        browser = 'Chrome'
    elif 'safari' in ua:
        browser = 'Safari'
    elif 'opera' in ua or 'opr' in ua:
        browser = 'Opera'
    else:
        browser = 'Unknown'
    return {'device': device, 'os': os, 'browser': browser}

router = APIRouter(tags=["redirect"])

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # 1. Найти ссылку
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    # 2. Увеличить счётчик кликов
    await crud.increment_clicks(db, link)

    # 3. Получить IP и User-Agent
    client_ip = request.client.host if request.client else None
    user_agent_str = request.headers.get("user-agent", "")

    # 4. Парсим User-Agent через Python
    ua_info = parse_user_agent_py(user_agent_str)

    # 5. Сохраняем клик в БД
    try:
        asyncio.create_task(save_click_background(
            link_id=link.id,
            ip=client_ip,
            user_agent=user_agent_str,
            device=ua_info['device'],
            os=ua_info['os'],
            browser=ua_info['browser']
        ))
    except Exception as e:
        print(f"Ошибка сохранения клика: {e}", flush=True)

    # 6. Редирект
    return RedirectResponse(url=link.original_url, status_code=302)



async def save_click_background(link_id: int, ip: str, user_agent: str, device: str, os: str, browser: str):
    """Сохраняет клик в отдельной сессии, не блокируя основной запрос."""
    start = time.time()
    print(f"⏳ Фоновая задача: начало сохранения клика в {start:.3f}", flush=True)
    async with AsyncSessionLocal() as db:
        try:
            await crud.save_click(
                db=db,
                link_id=link_id,
                ip=ip,
                user_agent=user_agent,
                device=device,
                os=os,
                browser=browser
            )
            end = time.time()
            print(f"✅ Фоновая задача: клик сохранён за {end - start:.3f} сек", flush=True)
        except Exception as e:
            end = time.time()
            print(f"❌ Ошибка фонового сохранения клика через {end - start:.3f} сек: {e}", flush=True)