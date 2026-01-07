# src/physics.py
import numpy as np
import pandas as pd
from scipy import stats

def calculate_square_root_law(df, bins=40):
    """
    Проверяет закон I ~ sqrt(Q).
    Возвращает словарь с результатами регрессии и данными для графика.
    """
    # 1. Фильтрация: берем только свечи, где была хоть какая-то волатильность
    df_clean = df[df['volatility'] > 0].copy()
    
    if len(df_clean) < 100:
        return None  # Слишком мало данных

    # 2. Логарифмирование
    # Y = log(Volatility), X = log(Volume)
    df_clean['log_Q'] = np.log(df_clean['volume'])
    df_clean['log_I'] = np.log(df_clean['volatility'])
    
    # 3. Биннинг (Binning) - группировка по объему
    # Создаем корзины равного размера
    try:
        df_clean['bin'] = pd.qcut(df_clean['volume'], bins, duplicates='drop')
    except ValueError:
        # Если данных мало и квартили схлопываются
        df_clean['bin'] = pd.cut(df_clean['volume'], bins)

    binned_data = df_clean.groupby('bin', observed=True)[['log_Q', 'log_I']].mean()
    
    # 4. Фильтр Smart Money (правая половина графика)
    # Отсекаем шум тиков (левую часть)
    median_vol = binned_data['log_Q'].median()
    smart_money_data = binned_data[binned_data['log_Q'] > median_vol].copy()
    
    if len(smart_money_data) < 3:
        return None

    # 5. Линейная регрессия
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