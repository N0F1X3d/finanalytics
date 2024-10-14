import httpx
import pandas as pd

def get_securities_list():
    urls = {
        "shares": "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json",  # Акции
        "bonds": "https://iss.moex.com/iss/engines/stock/markets/bonds/securities.json",   # Облигации
        #"funds": "https://iss.moex.com/iss/engines/stock/markets/funds/securities.json"    # Фонды (ETF и ПИФы)
    }
    
    all_securities = []

    with httpx.Client() as client:
        for market, url in urls.items():
            response = client.get(url)
            data = response.json()

            # Извлекаем данные о ценных бумагах
            securities_data = data['securities']['data']
            securities_columns = data['securities']['columns']

            # Преобразуем в DataFrame
            df = pd.DataFrame(securities_data, columns=securities_columns)

            # Оставляем только важные столбцы
            df = df[['SECID', 'SHORTNAME', 'BOARDID']]

            # Добавляем информацию о типе рынка
            df['MARKET'] = market

            # Преобразуем DataFrame в список словарей и добавляем к итоговому списку
            all_securities.extend(df.to_dict(orient='records'))

    return all_securities