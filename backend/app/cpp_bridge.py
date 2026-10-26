# backend/app/cpp_bridge.py
import ctypes
import os
import sys
import logging
import asyncio
import concurrent.futures
from pathlib import Path

#from ..cpp_bridge import get_test_string_cpp # для тестирования загрузки DLL

# ----------------------------------------------------------------------
# Настройка логирования
# ----------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------
# 1. Определяем пути
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CPP_MODULES_DIR = BASE_DIR / "cpp_modules"

# Папка для логов
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "cpp_parser.log"

# =========================================================================
# ЧАСТЬ 1: Генератор коротких кодов (работает)
# =========================================================================
DLL_PATH = CPP_MODULES_DIR / "generator.dll"
_generator_lib = None

logger.info(f"Базовая директория проекта: {BASE_DIR}")
logger.info(f"Папка с C++ модулями: {CPP_MODULES_DIR}")
logger.info(f"Полный путь к DLL генератора: {DLL_PATH}")

if not DLL_PATH.exists():
    logger.error(f"Файл {DLL_PATH} не существует!")
    _generator_lib = None
else:
    logger.info(f"Файл {DLL_PATH} найден. Размер: {DLL_PATH.stat().st_size} байт")
    if sys.platform == "win32":
        try:
            os.add_dll_directory(str(DLL_PATH.parent))
            mingw_bin = r"C:\msys64\ucrt64\bin"
            if os.path.exists(mingw_bin):
                os.add_dll_directory(mingw_bin)
        except Exception as e:
            logger.warning(f"Ошибка добавления пути для DLL: {e}")

    try:
        _generator_lib = ctypes.CDLL(str(DLL_PATH))
        logger.info("✅ DLL генератора загружена!")
        _generator_lib.generate_code.argtypes = [ctypes.c_int]
        _generator_lib.generate_code.restype = ctypes.c_char_p
        _generator_lib.free_string.argtypes = [ctypes.c_void_p]
        _generator_lib.free_string.restype = None
        logger.info("✅ Функции генератора настроены.")
    except Exception as e:
        logger.error(f"Ошибка загрузки DLL генератора: {e}")
        _generator_lib = None

def generate_short_code_cpp(length: int = 6) -> str | None:
    if _generator_lib is None:
        return None
    try:
        ptr = _generator_lib.generate_code(length)
        if ptr:
            code = ptr.decode('utf-8')
            _generator_lib.free_string(ptr)
            return code
    except Exception as e:
        logger.error(f"Ошибка вызова C++ генератора: {e}")
    return None

# =========================================================================
# ЧАСТЬ 2: Парсер User-Agent (потокобезопасная версия)
# =========================================================================
USERAGENT_DLL_PATH = CPP_MODULES_DIR / "useragent.dll"

# Пул потоков (один экземпляр)
_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def _call_cpp_parser_in_thread(user_agent: str) -> dict | None:
    """Вызывается в отдельном потоке, загружает DLL и парсит UA."""
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"Thread called with UA: {user_agent[:50]}\n")

        # Загружаем DLL (каждый поток загружает свою копию – безопасно)
        if not USERAGENT_DLL_PATH.exists():
            with open(LOG_FILE, "a") as f:
                f.write("DLL not found\n")
            return None

        lib = ctypes.CDLL(str(USERAGENT_DLL_PATH))
        lib.parse_user_agent.argtypes = [ctypes.c_char_p]
        lib.parse_user_agent.restype = ctypes.c_char_p
        lib.free_string.argtypes = [ctypes.c_void_p]
        lib.free_string.restype = None

        ptr = lib.parse_user_agent(user_agent.encode('utf-8'))
        if not ptr:
            with open(LOG_FILE, "a") as f:
                f.write("ptr is NULL\n")
            return None
        result_str = ptr.decode('utf-8')
        lib.free_string(ptr)
        parts = result_str.split('|')
        if len(parts) == 3:
            with open(LOG_FILE, "a") as f:
                f.write(f"Parsed: {parts}\n")
            return {"device": parts[0], "os": parts[1], "browser": parts[2]}
        else:
            with open(LOG_FILE, "a") as f:
                f.write(f"Invalid parts: {parts}\n")
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"Exception in thread: {e}\n")
    return None

async def parse_user_agent_cpp(user_agent: str) -> dict | None:
    """Асинхронная обёртка, запускающая C++ парсер в отдельном потоке."""
    loop = asyncio.get_event_loop()
    try:
        # Запускаем синхронную функцию в потоке
        result = await loop.run_in_executor(_thread_pool, _call_cpp_parser_in_thread, user_agent)
        return result
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"Exception in executor: {e}\n")
        return None
    



# =========================================================================
# ТЕСТОВАЯ ЧАСТЬ: простая DLL
# =========================================================================
SIMPLE_DLL_PATH = CPP_MODULES_DIR / "simple.dll"
_simple_lib = None

if SIMPLE_DLL_PATH.exists():
    try:
        _simple_lib = ctypes.CDLL(str(SIMPLE_DLL_PATH))
        _simple_lib.get_test_string.argtypes = []
        _simple_lib.get_test_string.restype = ctypes.c_char_p
        _simple_lib.free_string.argtypes = [ctypes.c_void_p]
        _simple_lib.free_string.restype = None
        print("✅ Тестовая DLL simple.dll загружена", flush=True)
    except Exception as e:
        print(f"❌ Ошибка загрузки simple.dll: {e}", flush=True)
else:
    print(f"⚠️ Файл {SIMPLE_DLL_PATH} не найден", flush=True)

def get_test_string_cpp() -> str | None:
    """Тестовая функция: вызывает простую DLL и возвращает строку"""
    if _simple_lib is None:
        return None
    try:
        ptr = _simple_lib.get_test_string()
        if ptr:
            result = ptr.decode('utf-8')
            _simple_lib.free_string(ptr)
            return result
    except Exception as e:
        print(f"Ошибка вызова get_test_string: {e}", flush=True)
    return None