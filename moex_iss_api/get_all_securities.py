import requests
import pandas as pd

def get_securities_list():
    with requests.Session() as session:
        url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json"
        response = session.get(url)
        data = response.json()

        # Извлекаем данные о ценных бумагах
        securities_data = data['securities']['data']
        securities_columns = data['securities']['columns']

        # Преобразуем в DataFrame
        df = pd.DataFrame(securities_data, columns=securities_columns)

        # Оставляем только важные столбцы
        df = df[['SECID', 'SHORTNAME', 'BOARDID']]

        # Преобразуем DataFrame в список словарей
        securities_list = df.to_dict(orient='records')
        
        return securities_list
