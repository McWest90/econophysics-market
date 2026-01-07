# src/config.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# --- ПУТИ ---
# Определяем корневую папку проекта
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Создаем папку data, если её нет
DATA_DIR.mkdir(exist_ok=True)

# --- НАСТРОЙКИ API ---
TOKEN = os.getenv("T_BANK_TOKEN")
APP_NAME = "econophysics-research"

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(APP_NAME)

# Проверка токена
if not TOKEN:
    logger.warning("⚠️ Токен T_BANK_TOKEN не найден в .env! Скачивание данных работать не будет.")