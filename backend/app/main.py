# backend/app/main.py


import logging

# Настройка логирования для корневого логгера, чтобы видеть наши сообщения
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, links, redirect

app = FastAPI(title="URL Shortener API")

# Разрешаем CORS для фронтенда (React на localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # адрес, где будет работать React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(links.router)
app.include_router(redirect.router)

@app.get("/")
async def root():
    return {"message": "URL Shortener API is running"}