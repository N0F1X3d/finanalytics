import httpx
import pandas as pd
from mainview.models import Security, Bond
import datetime

def get_securities_list():
    urls = {
        "shares": "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json",  # Акции
        "bonds": "https://iss.moex.com/iss/engines/stock/markets/bonds/securities.json",   # Облигации
    }

    with httpx.Client() as client:
        for market, url in urls.items():
            response = client.get(url)
            data = response.json()

            # Извлекаем данные о ценных бумагах
            securities_data = data['securities']['data']
            securities_columns = data['securities']['columns']

            # Преобразуем в DataFrame
            df = pd.DataFrame(securities_data, columns=securities_columns)
            # Оставляем только важные столбцы и сохраняем их в базу данных
            match market:
                case 'shares':
                    df = df[['SECID', 'SHORTNAME', 'PREVPRICE']]
                    df['PREVPRICE'] = df['PREVPRICE'].fillna(0.0)
                    # Проход по каждой строке DataFrame
                    for _, row in df.iterrows():
                        if row['PREVPRICE'] > 0.0:
                            Security.objects.update_or_create(
                                ticker=row['SECID'],
                                defaults={
                                    'name': row['SHORTNAME'],
                                    'current_price': row['PREVPRICE'],
                                }
                            )
                case 'bonds':
                    df = df[['SECID', 'SHORTNAME', 'COUPONPERCENT', 'MATDATE']]
                    df['COUPONPERCENT'] = df['COUPONPERCENT'].fillna(0.0)
                    df = df[df['MATDATE'] >= str(datetime.date.today())]
                    
                    # Проход по каждой строке DataFrame
                    for _, row in df.iterrows():
                        if row['COUPONPERCENT'] > 0.0:
                            Bond.objects.update_or_create(
                                ticker=row['SECID'],
                                defaults={
                                    'name': row['SHORTNAME'],
                                    'current_price': row['COUPONPERCENT'],
                                }
                            )
