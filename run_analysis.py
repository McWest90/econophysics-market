# run_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from src.config import DATA_DIR
from src.physics import calculate_square_root_law

# Какие файлы анализируем
TICKERS = ["SBER", "FLOT", "SELG"]

def main():
    print("🔬 Запуск физического анализатора...")
    
    for ticker in TICKERS:
        file_path = DATA_DIR / f"{ticker}_1min.csv"
        
        if not file_path.exists():
            print(f"⚠️ Данные для {ticker} не найдены. Сначала запустите run_collection.py")
            continue
            
        # 1. Читаем
        df = pd.read_csv(file_path)
        
        # 2. Считаем физику (импорт из src/physics.py)
        res = calculate_square_root_law(df)
        
        if not res:
            print(f"❌ {ticker}: Недостаточно данных для анализа.")
            continue
            
        # 3. Печатаем результат в консоль
        alpha = res['alpha']
        r2 = res['r2']
        status = "✅ CONFIRMED" if (0.4 <= alpha <= 0.6 and r2 > 0.9) else "⚠️ ANOMALY"
        
        print(f"\n📊 АКТИВ: {ticker}")
        print(f"   Alpha (Наклон): {alpha:.4f}")
        print(f"   R^2 (Точность): {r2:.4f}")
        print(f"   Вердикт: {status}")
        
        # 4. Рисуем график
        plot_results(ticker, res, status)

def plot_results(ticker, res, status):
    plt.figure(figsize=(10, 6))
    
    # Фон (серые точки)
    plt.scatter(res['raw_data']['log_Q'], res['raw_data']['log_I'], 
                alpha=0.05, color='#CCCCCC', label='Raw Noise')
    
    # Усредненные бины (красные)
    plt.scatter(res['binned_data']['log_Q'], res['binned_data']['log_I'], 
                color='red', s=30, label='Binned Avg')
    
    # Умные деньги (зеленые)
    sm = res['smart_money']
    plt.scatter(sm['log_Q'], sm['log_I'], color='lime', s=80, edgecolors='black', label='Smart Money')
    
    # Линия тренда
    slope, intercept = res['params']
    x_vals = np.linspace(sm['log_Q'].min(), sm['log_Q'].max(), 100)
    y_vals = slope * x_vals + intercept
    plt.plot(x_vals, y_vals, color='blue', linewidth=3, label=f'Fit (k={slope:.2f})')
    
    plt.title(f"Market Impact Law: {ticker}\nStatus: {status} (R2={res['r2']:.2f})")
    plt.xlabel("Log(Volume) [Энергия]")
    plt.ylabel("Log(High - Low) [Волатильность]")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Чтобы график не блокировал выполнение, можно сохранять его, а не показывать
    # plt.savefig(f"data/{ticker}_result.png") 
    plt.show() 

if __name__ == "__main__":
    main()