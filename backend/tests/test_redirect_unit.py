# backend/tests/test_redirect_unit.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.routers.redirect import redirect_to_original
from app.schemas import LinkOut

@pytest.mark.asyncio
async def test_redirect_success():
    # Создаём мок для сессии БД
    mock_db = AsyncMock()
    # Мок для crud.get_link_by_code – возвращает существующую ссылку
    mock_link = MagicMock()
    mock_link.original_url = "https://example.com"
    mock_link.id = 1
    # Подменяем crud в модуле redirect (нужно импортировать crud внутри теста)
    import app.routers.redirect as redirect_module
    redirect_module.crud.get_link_by_code = AsyncMock(return_value=mock_link)
    redirect_module.crud.increment_clicks = AsyncMock()
    redirect_module.crud.save_click = AsyncMock()
    
    # Создаём мок для Request
    mock_request = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.headers.get.return_value = "Test User-Agent"

    # Вызываем функцию
    response = await redirect_to_original("abc123", mock_request, mock_db)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com"
    # Проверяем, что инкремент был вызван
    redirect_module.crud.increment_clicks.assert_awaited_once()

@pytest.mark.asyncio
async def test_redirect_not_found():
    import app.routers.redirect as redirect_module
    redirect_module.crud.get_link_by_code = AsyncMock(return_value=None)
    mock_db = AsyncMock()
    mock_request = MagicMock()
    with pytest.raises(HTTPException) as exc:
        await redirect_to_original("missing", mock_request, mock_db)
    assert exc.value.status_code == 404