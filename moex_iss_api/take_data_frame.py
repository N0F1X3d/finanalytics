import requests
import apimoex
import pandas as pd

with requests.Session() as session:
    # Устанавливаем параметры для запроса
    url = 'https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/SBER.json'
    params = {
        'from': '2023-01-01',  # начиная с этой даты
        'till': '2023-12-31',  # до этой даты
    }
    
    # Получаем данные
    response = session.get(url, params=params)
    
    # Преобразуем данные в JSON
    data = response.json()
    
    # Извлекаем данные из таблицы "history" и "columns" для соответствия столбцов
    history_data = data['history']['data']
    history_columns = data['history']['columns']
    
    # Преобразуем в DataFrame для удобства
    df = pd.DataFrame(history_data, columns=history_columns)
    
    # Выводим первые несколько строк
    print(df.head())
