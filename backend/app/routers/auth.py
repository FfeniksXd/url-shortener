# backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from .. import schemas, crud, auth  
from ..database import get_db  

#2FA imports
import pyotp
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse 
from jose import jwt, JWTError


router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=schemas.UserOut)
async def register(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    Принимает email и пароль, возвращает данные пользователя.
    """
    # Проверяем, не занят ли email
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # Создаём пользователя
    return await crud.create_user(db, user)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    print(f"User {user.email}, is_2fa_enabled={user.is_2fa_enabled}")

    if user.is_2fa_enabled:
        # Создаём временный токен (действует 5 минут)
        temp_token = auth.create_access_token(
            data={"sub": user.email, "temp": True},
            expires_delta=timedelta(minutes=5)
        )
        return {"need_2fa": True, "temp_token": temp_token}
    else:
        access_token = auth.create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

#2FA endpoints
@router.get("/enable-2fa")
async def enable_2fa(
    current_user: schemas.UserOut = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Если секрета ещё нет, генерируем
    if not current_user.totp_secret:
        secret = pyotp.random_base32()
        current_user.totp_secret = secret
        await db.commit()
    else:
        secret = current_user.totp_secret

    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(current_user.email, issuer_name="URLShortener")

    img = qrcode.make(provisioning_uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

@router.post("/verify-2fa-login")
async def verify_2fa_login(
    temp_token: str,
    code: str,
    db: AsyncSession = Depends(get_db)
):
    # Декодируем временный токен
    try:
        payload = jwt.decode(temp_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
        is_temp = payload.get("temp")
        if not email or not is_temp:
            raise HTTPException(status_code=400, detail="Invalid temporary token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid temporary token")

    user = await crud.get_user_by_email(db, email)
    if not user or not user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Invalid code")

    # Всё правильно — выдаём постоянный токен
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/disable-2fa")
async def disable_2fa(
    current_user: schemas.UserOut = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_user.is_2fa_enabled = False
    current_user.totp_secret = None
    await db.commit()
    return {"message": "2FA disabled"}

@router.get("/2fa-status")
async def get_2fa_status(
    current_user: schemas.UserOut = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_email(db, current_user.email)
    return {"is_2fa_enabled": user.is_2fa_enabled}