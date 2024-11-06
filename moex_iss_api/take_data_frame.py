import requests
import apimoex
from datetime import date, timedelta
import pandas as pd
import plotly.express as px

def get_chart_html(ticker):
    # Создаем сессию
    with requests.Session() as session:
        interval = 4
        # Получаем данные с помощью apimoex
        #end = 
        #start = 
        data = apimoex.get_market_candles(session=session, security=ticker, interval=interval)
        df = pd.DataFrame(data)
        df['begin'] = pd.to_datetime(df['begin'])

        # Строим график
        fig = px.line(df, x='begin', y='close', title='Closing Prices Over Time', labels={'begin': 'Date', 'close': 'Closing Price'})
        
        # Возвращаем график в формате HTML
        return fig.to_html(full_html=False)
