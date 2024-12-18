import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from mainview.models import Data
import plotly.express as px

def get_stock_data(ticker):
    # Получение данных
    data = Data.objects.filter(security__ticker=ticker).order_by('date_time')
    if not data.exists():
        raise ValueError(f"No data found for ticker {ticker}")
    
    # Преобразуем queryset в DataFrame
    df = pd.DataFrame.from_records(data.values('date_time', 'price'))
    df['date_time'] = pd.to_datetime(df['date_time'])

    # Добавляем скользящие средние
    df['SMA_20'] = df['price'].rolling(window=20).mean()
    df['EMA_20'] = df['price'].ewm(span=20, adjust=False).mean()

    # Нормализация цен
    scaler = MinMaxScaler()
    df['normalized_price'] = scaler.fit_transform(df['price'].values.reshape(-1, 1))
    
    return df, scaler


def create_sequences(data, seq_length=225):
    # Преобразование данных в последовательности для обучения модели
    sequences = []
    targets = []
    for i in range(len(data) - seq_length):
        sequences.append(data[i:i + seq_length])
        targets.append(data[i + seq_length])
    return np.array(sequences), np.array(targets)

def build_lstm(input_shape):
    model = Sequential([
        # Первый LSTM слой
        LSTM(256, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        
        # Второй LSTM слой
        LSTM(256, return_sequences=True),
        Dropout(0.3),
        
        # Третий LSTM слой
        LSTM(128, return_sequences=True),
        Dropout(0.3),
        
        # Четвёртый LSTM слой
        LSTM(64, return_sequences=True),
        Dropout(0.3),
        
        # Пятый LSTM слой
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        
        # Первый Dense слой
        Dense(128, activation='relu'),
        Dropout(0.2),
        
        # Второй Dense слой
        Dense(64, activation='relu'),
        Dropout(0.2),
        
        # Третий Dense слой
        Dense(32, activation='relu'),
        Dropout(0.1),
        
        # Выходной слой
        Dense(1)
    ])
    # Компиляция модели с более низкой скоростью обучения
    optimizer = Adam(learning_rate=0.0001)
    model.compile(optimizer=optimizer, loss='mean_squared_error')
    return model


def train_and_predict(ticker, seq_length=225, future_days=7):
    # Получение данных
    df, scaler = get_stock_data(ticker)
    prices = df['normalized_price'].values
    X, y = create_sequences(prices, seq_length)

    # Разделение данных на обучающую и тестовую выборки
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Добавление размерности для LSTM (последовательность, шаги, признаки)
    X_train = X_train[..., np.newaxis]
    X_test = X_test[..., np.newaxis]

    # Обучение модели
    model = build_lstm((X_train.shape[1], X_train.shape[2]))
    model.fit(X_train, y_train, batch_size=64, epochs=25, verbose=1)

    # Итеративное предсказание на future_days
    future_predictions = []
    last_sequence = X_test[-1]  # Берём последнюю последовательность из тестовых данных

    for _ in range(future_days):
        # Предсказываем следующее значение
        next_price = model.predict(last_sequence[np.newaxis, ...])[0][0]
        future_predictions.append(next_price)

        # Обновляем последовательность
        next_sequence = np.append(last_sequence[1:], [[next_price]], axis=0)
        last_sequence = next_sequence

    # Масштабируем предсказания обратно к исходным значениям
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1)).flatten()


    # Получение последней реальной цены и даты
    last_real_date = df['date_time'].iloc[-1]
    last_real_price = df['price'].iloc[-1]

    # Возвращаем результаты
    return last_real_date, last_real_price, last_real_date + pd.to_timedelta(range(1, future_days + 1), unit='D'), future_predictions

def generate_future_graph(ticker, last_date, last_price, future_dates, future_prices):
    # Создаем DataFrame для графика
    df = pd.DataFrame({
        'Дата': [last_date] + list(future_dates),
        'Цена': [last_price] + list(future_prices)
    })

    # Создание графика
    fig = px.line(df, x='Дата', y='Цена', title=f'Прогноз цен на 7 дней для {ticker}', labels={'Дата': 'Дата', 'Цена': 'Цена'})
    fig.update_traces(line=dict(color='green'))
    fig.update_layout(
        title=f'Прогноз цен на 7 дней для {ticker}',
        xaxis_title='Дата',
        yaxis_title='Цена',
        template='plotly_dark'
    )
    return fig.to_html(full_html=False)
