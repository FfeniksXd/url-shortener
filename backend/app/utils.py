# backend/app/utils.py
import random
import string
import logging
from .cpp_bridge import generate_short_code_cpp

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_short_code(length: int = 6) -> str:
    print("=== generate_short_code called ===", flush=True)
    code = generate_short_code_cpp(length)
    if code is not None:
        logger.info("🔵 Используется C++ генератор, код: %s", code)
        return code

    # Fallback на Python
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    logger.warning("🟡 Используется Python (fallback), код: %s", code)
    return code