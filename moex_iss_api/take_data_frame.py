import requests
import apimoex
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from mainview.models import Data, Security
from django.db.models.functions import Length

def get_chart_html(ticker, start=datetime.now().date() - timedelta(days=1), end=datetime.now().date()):
    # Вычисляем разницу в днях
    date_diff = (end - start).days
    interval = 1
    
    # Определяем интервал в зависимости от разницы в днях
    if date_diff <= 1:
        interval = 1  # 1 минута
    elif date_diff <= 4:
        interval = 10  # 10 минут
    elif date_diff <= 7:
        interval = 60  # 1 час
    elif date_diff <= 30:
        interval = 24  # 1 день
    elif date_diff <= 180:
        interval = 7  # 1 неделя
    elif date_diff <= 366:
        interval = 31  # месяц
    else:
        interval = 4  # 1 квартал

    # Создаем сессию
    with requests.Session() as session:
        # Получаем данные с помощью apimoex
        data = apimoex.get_market_candles(session=session, security=ticker, interval=interval, start=start, end=end)
        df = pd.DataFrame(data)
        df['begin'] = pd.to_datetime(df['begin'])

        # Убедимся, что для заданных start и end дат есть данные
        start_data = df.iloc[0]
        end_data = df.iloc[-1]

        # Проверяем, были ли найдены данные для start и end
        if start_data is None or end_data is None:
            return "Нет данных для выбранного диапазона дат."

        # Получаем цены закрытия на начало и конец
        start_price = start_data['close']
        end_price = end_data['close']


        # Определяем цвет линии и заливки
        if start_price < end_price:
            color = 'green'
            fill_color = 'rgba(0, 255, 0, 0.3)'
        else:
            color = 'red'
            fill_color = 'rgba(255, 0, 0, 0.3)'

        # Строим график
        fig = px.line(df, x='begin', y='close', title=f'График цен для {ticker}', labels={'begin': 'Дата', 'close': 'Цена закрытия'})

        # Изменяем цвет линии
        fig.update_traces(line=dict(color=color))

        # Добавляем заливку под графиком
        fig.update_traces(fill='tozeroy', fillcolor=fill_color)

        # Центрируем график по оси Y, устанавливая диапазон оси с небольшим отступом от максимума и минимума
        y_min = df['close'].min() * 0.95  # Мин цена с 5% отступом
        y_max = df['close'].max() * 1.05  # Макс цена с 5% отступом
        fig.update_layout(yaxis=dict(range=[y_min, y_max]))

        # Возвращаем график в формате HTML
        return fig.to_html(full_html=False)


def get_left_border(ticker):
    with requests.Session() as session:
        data = apimoex.get_market_candle_borders(session=session, security=ticker)
        if not data:
            return None  
        df = pd.DataFrame(data)
        df['begin'] = pd.to_datetime(df['begin'])
        left_border = df['begin'][0]
        return left_border

def fill_data():
    securities = Security.objects.annotate(ticker_length=Length('ticker')).filter(ticker_length__lte=4)
    Data.objects.all().delete()
    with requests.Session() as session:
        for security in securities:
            data = apimoex.get_market_candles(session=session, security=security.ticker, interval=24, start=datetime.now().date()-timedelta(days=365), end=datetime.now().date())
            df = pd.DataFrame(data)
            
            # Проверка: если df пустой, переход к следующему тикеру
            if df.empty:
                print(f"No data available for ticker {security.ticker}")
                continue
            
            # Если df не пустой, преобразуем столбец 'begin' в тип datetime
            df['begin'] = pd.to_datetime(df['begin'])
            
            for _, row in df.iterrows():
                Data.objects.create(
                    security=security,
                    date_time=row['begin'],
                    price=row['close']
                )

def fill_data_every_day():
    securities = Security.objects.annotate(ticker_length=Length('ticker')).filter(ticker_length__lte=4)
    with requests.Session() as session:
        for security in securities:
            data = apimoex.get_market_candles(session=session, security=security.ticker, interval=24, start=datetime.now().date() - timedelta(days=1), end=datetime.now().date())
            df = pd.DataFrame(data)
            
            # Проверка: если df пустой, переход к следующему тикеру
            if df.empty:
                print(f"No data available for ticker {security.ticker}")
                continue
            
            # Если df не пустой, преобразуем столбец 'begin' в тип datetime
            df['begin'] = pd.to_datetime(df['begin'])
            
            for _, row in df.iterrows():
                Data.objects.create(
                    security=security,
                    date_time=row['begin'],
                    price=row['close']
                )