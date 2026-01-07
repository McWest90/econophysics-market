# run_collection.py
from src.loader import download_data

# Список тикеров для исследования
# SBER, FLOT, SELG - наши доказательства
# KMAZ - наша аномалия
TICKERS_TO_DOWNLOAD = ["SBER", "FLOT", "SELG"]

if __name__ == "__main__":
    print("🚀 Запуск сборщика данных...")
    
    for ticker in TICKERS_TO_DOWNLOAD:
        # days_back=60 гарантирует захват рабочих дней декабря
        download_data(ticker, days_back=60)
        
    print("🏁 Сбор данных завершен. Проверьте папку data/")