import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from mainview.models import Data
import plotly.express as px

def get_stock_data(ticker):
    # Получение данных для акций из базы данных
    data = Data.objects.filter(security__ticker=ticker).order_by('date_time')
    if not data.exists():
        raise ValueError(f"No data found for ticker {ticker}")
    
    # Преобразуем queryset в DataFrame
    df = pd.DataFrame.from_records(data.values('date_time', 'price'))

    # Проверка исходных данных
    print(df['date_time'].head())  # Печать первых нескольких значений

    # Преобразуем 'date_time' в datetime, если это необходимо
    df['date_time'] = pd.to_datetime(df['date_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

    # Проверка на наличие некорректных дат
    if df['date_time'].isnull().any():
        invalid_dates = df[df['date_time'].isnull()]
        print(f"Некорректные даты: {invalid_dates}")  # Печать некорректных дат
        raise ValueError("Некорректные значения в столбце date_time")

    # Нормализация цен
    scaler = MinMaxScaler(feature_range=(0, 1))
    df['normalized_price'] = scaler.fit_transform(df['price'].values.reshape(-1, 1))
    
    return df, scaler

def create_sequences(data, seq_length=60):
    # Преобразование данных в последовательности для обучения модели
    sequences = []
    targets = []
    for i in range(len(data) - seq_length):
        sequences.append(data[i:i + seq_length])
        targets.append(data[i + seq_length])
    return np.array(sequences), np.array(targets)

def build_lstm(input_shape):
    # Построение модели LSTM
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_and_predict(ticker, seq_length=60):
    # Получение данных
    df, scaler = get_stock_data(ticker)
    prices = df['normalized_price'].values
    X, y = create_sequences(prices, seq_length)

    # Разделение данных на обучающую и тестовую выборки
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Обучение модели
    model = build_lstm((X_train.shape[1], 1))
    model.fit(X_train, y_train, batch_size=32, epochs=10, verbose=1)

    # Получение предсказаний
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    real_prices = scaler.inverse_transform(y_test.reshape(-1, 1))

    return real_prices, predictions

def generate_graph(ticker, predicted_prices, dates):
    # Убедимся, что predicted_prices одномерный массив
    predicted_prices = np.array(predicted_prices).flatten()

    # Проверка и преобразование dates в подходящий формат
    if isinstance(dates, (np.ndarray, list)):
        dates = pd.to_datetime(dates, errors='coerce')  # Преобразуем в datetime, если это нужно
    elif isinstance(dates, pd.Series):
        # Если это уже Series, то можно оставить как есть
        dates = pd.to_datetime(dates, errors='coerce')  # Для уверенности
    else:
        raise TypeError(f"Некорректный тип для даты: {type(dates)}")

    # Проверка на наличие некорректных значений
    if dates.isnull().any():  # Проверяем на NaT (некорректные даты)
        print(f"Некорректные даты: {dates[dates.isnull()]}")
        raise ValueError("Некорректные даты найдены в данных")

    # Проверка соответствия длины данных
    if len(dates) != len(predicted_prices):
        raise ValueError("Количество дат не совпадает с количеством предсказанных цен")

    # Создаем DataFrame для предсказанных цен с датами
    df = pd.DataFrame({
        'Дата': dates,  # Даты уже в формате datetime
        'Предсказанная цена': predicted_prices
    })

    # Создание графика с использованием Plotly Express
    try:
        fig = px.line(df, x='Дата', y='Предсказанная цена', title=f'Прогноз цен для {ticker}', labels={'Дата': 'Дата', 'Предсказанная цена': 'Цена'})
    except Exception as e:
        print(f"Ошибка при создании графика: {e}")
        raise

    # Настройка внешнего вида графика
    fig.update_traces(line=dict(color='royalblue'))  # Цвет линии
    fig.update_layout(
        title=f'Прогноз цен для {ticker}',
        xaxis_title='Дата',
        yaxis_title='Цена',
        template='plotly_dark'  # Вы можете выбрать другую тему
    )

    # Генерация HTML для графика
    graph_html = fig.to_html(full_html=False)

    return graph_html
