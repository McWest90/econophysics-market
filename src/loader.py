# src/loader.py
import time
import pandas as pd
from datetime import timedelta
from decimal import Decimal
from t_tech.invest import Client, CandleInterval
from t_tech.invest.utils import now, quotation_to_decimal
from t_tech.invest.exceptions import RequestError # Импортируем ошибку для перехвата

from src.config import TOKEN, DATA_DIR, logger

def get_instrument_uid(client, ticker, class_code='TQBR'):
    """Находит UID инструмента по тикеру."""
    try:
        instruments = client.instruments.find_instrument(query=ticker).instruments
        for item in instruments:
            if item.ticker == ticker and item.class_code == class_code:
                logger.info(f"🔎 Инструмент найден: {item.name} (UID: {item.uid})")
                return item.uid
        logger.error(f"❌ Инструмент {ticker} не найден в режиме {class_code}")
        return None
    except Exception as e:
        logger.error(f"Ошибка поиска инструмента: {e}")
        return None

def download_data(ticker, days_back=60, class_code='TQBR'):
    """
    Скачивает свечи с механизмом повторных попыток (Retry).
    """
    if not TOKEN:
        logger.error("Нет токена. Прерывание.")
        return

    # Проверка: если файл уже есть, можно пропустить (раскомментируйте, если хотите экономить время)
    # file_path = DATA_DIR / f"{ticker}_1min.csv"
    # if file_path.exists():
    #     logger.info(f"⏭️ Файл {ticker} уже существует. Пропуск.")
    #     return

    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:
            logger.info(f"🚀 Загрузка {ticker} (Попытка {attempt + 1}/{max_retries})...")
            
            with Client(TOKEN) as client:
                uid = get_instrument_uid(client, ticker, class_code)
                if not uid:
                    return # Если UID нет, ретраить бесполезно

                candles_data = []
                # Скачиваем
                for candle in client.get_all_candles(
                    instrument_id=uid,
                    from_=now() - timedelta(days=days_back),
                    interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
                ):
                    candles_data.append({
                        'time': candle.time,
                        'open': float(quotation_to_decimal(candle.open)),
                        'close': float(quotation_to_decimal(candle.close)),
                        'high': float(quotation_to_decimal(candle.high)),
                        'low': float(quotation_to_decimal(candle.low)),
                        'volume': candle.volume,
                        'is_complete': candle.is_complete
                    })

            # Если мы дошли сюда, значит ошибок не было
            if not candles_data:
                logger.warning(f"Данные по {ticker} пусты!")
                return

            # Создаем DataFrame и сохраняем
            df = pd.DataFrame(candles_data)
            df['volatility'] = df['high'] - df['low']
            
            file_path = DATA_DIR / f"{ticker}_1min.csv"
            df.to_csv(file_path, index=False)
            
            logger.info(f"💾 Успешно сохранено: {file_path} ({len(df)} строк)")
            return # Выход из функции (успех)

        except RequestError as e:
            logger.warning(f"⚠️ Ошибка сети при скачивании {ticker}: {e}")
            logger.info("⏳ Ждем 5 секунд и пробуем снова...")
            time.sleep(5)
            attempt += 1
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            return # Неизвестная ошибка - выходим

    logger.error(f"⛔ Не удалось скачать {ticker} после {max_retries} попыток.")