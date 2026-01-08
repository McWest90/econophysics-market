# notebooks/check_hypothesis.py
import sys
import os
from pathlib import Path

current_dir = Path(os.getcwd())
project_root = current_dir.parent
sys.path.append(str(project_root))

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from src.config import DATA_DIR
from src.physics import calculate_square_root_law

TICKERS = ["SBER", "FLOT", "SELG"]

for ticker in TICKERS:
    file_path = DATA_DIR / f"{ticker}_1min.csv"
    
    if not file_path.exists():
        print(f"Файл {file_path} не найден. Сначала запустите загрузку.")
        continue
        
    df = pd.read_csv(file_path)
    
    res = calculate_square_root_law(df)
    
    if not res:
        print(f"Недостаточно данных для {ticker}")
        continue
        
    alpha = res['alpha']
    r2 = res['r2']
    
    print(f"--- {ticker} ---")
    print(f"Alpha: {alpha:.4f}")
    print(f"R^2:   {r2:.4f}")
    
    plt.figure(figsize=(10, 6))
    
    plt.scatter(res['raw_data']['log_Q'], res['raw_data']['log_I'], 
                alpha=0.05, color='gray', label='Raw Data')
    

    plt.scatter(res['binned_data']['log_Q'], res['binned_data']['log_I'], 
                color='red', label='Binned Data')
    
    sm = res['smart_money']
    plt.scatter(sm['log_Q'], sm['log_I'], color='lime', s=80, label='Smart Money')
    
    slope, intercept = res['params']
    x_vals = np.linspace(sm['log_Q'].min(), sm['log_Q'].max(), 100)
    y_vals = slope * x_vals + intercept
    plt.plot(x_vals, y_vals, color='blue', linewidth=3, label=f'Fit (k={slope:.2f})')
    
    plt.title(f"Market Impact Law: {ticker}\nAlpha={alpha:.3f}, R2={r2:.3f}")
    plt.xlabel("Log(Volume)")
    plt.ylabel("Log(High - Low)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()