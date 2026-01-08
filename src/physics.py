# src/physics.py
import numpy as np
import pandas as pd
from scipy import stats

def calculate_square_root_law(df, bins=40):
    """
    Проверяет закон I ~ sqrt(Q).
    Возвращает словарь с результатами регрессии и данными для графика.
    """
    df_clean = df[df['volatility'] > 0].copy()
    
    if len(df_clean) < 100:
        return None 


    df_clean['log_Q'] = np.log(df_clean['volume'])
    df_clean['log_I'] = np.log(df_clean['volatility'])
    
    try:
        df_clean['bin'] = pd.qcut(df_clean['volume'], bins, duplicates='drop')
    except ValueError:
        df_clean['bin'] = pd.cut(df_clean['volume'], bins)

    binned_data = df_clean.groupby('bin', observed=True)[['log_Q', 'log_I']].mean()
    
    median_vol = binned_data['log_Q'].median()
    smart_money_data = binned_data[binned_data['log_Q'] > median_vol].copy()
    
    if len(smart_money_data) < 3:
        return None

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        smart_money_data['log_Q'], smart_money_data['log_I']
    )
    
    return {
        'alpha': slope,          # Коэффициент (должен быть ~0.5)
        'r2': r_value**2,        # Точность
        'binned_data': binned_data,       # Все усредненные точки
        'smart_money': smart_money_data,  # Точки, по которым строили прямую
        'params': (slope, intercept),     # Параметры линии y = kx + b
        'raw_data': df_clean              # Сырые точки (для фона графика)
    }