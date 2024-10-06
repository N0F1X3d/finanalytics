import apimoex
from datetime import date, timedelta
import requests
import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.embed import components

def get_script_div(ticker):
        with requests.Session() as session:
            start_date = (date.today() - timedelta(days=365)).strftime('%Y-%m-%d')
            end_date = date.today().strftime('%Y-%m-%d')
            data = apimoex.get_market_history(session= session, security=ticker, start=start_date, end=end_date)
            df = pd.DataFrame(data)
            df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'])
            df_tqbr = df[df['BOARDID'] == 'TQBR']
            source = ColumnDataSource(df_tqbr)
            p = figure(x_axis_type="datetime", title=f"{ticker} Closing Prices Over Last Year", 
                        height=400, width=800)  # Используем height и width вместо plot_height и plot_width

            # Добавляем линию (TRADEDATE по оси X и CLOSE по оси Y)
            p.line(x='TRADEDATE', y='CLOSE', source=source, line_width=2, color='navy', alpha=0.7)

            # Настройка осей
            p.xaxis.axis_label = "Date"
            p.yaxis.axis_label = "Price (CLOSE)"
            script, div = components(p)
            return script, div