from datetime import datetime, timedelta
from django.db.models import F, FloatField, ExpressionWrapper
from mainview.models import Data, Security

def get_leaders_rising():
    # Определяем временной период для анализа
    time_period = datetime.now() - timedelta(days=7)
    securities = Security.objects.all()

    growth_leaders = []
    for security in securities:
        # Находим начальную цену (самая ранняя дата в периоде)
        start_data = Data.objects.filter(security=security, date_time__gte=time_period).order_by('date_time').first()
        # Находим конечную цену (самая поздняя дата в периоде)
        end_data = Data.objects.filter(security=security, date_time__gte=time_period).order_by('-date_time').first()

        # Проверяем, что есть данные для обеих дат
        if start_data and end_data:
            start_price = start_data.price
            end_price = end_data.price
            # Вычисляем процент изменения
            change = ((end_price - start_price) / start_price) * 100
            growth_leaders.append({
                'ticker': security.ticker,
                'start_price': start_price,
                'end_price': end_price,
                'change': change
            })

    # Сортируем по росту и отбираем топ-10
    growth_leaders = sorted(growth_leaders, key=lambda x: x['change'], reverse=True)[:10]
    return growth_leaders

def get_leaders_falling():
    # Определяем временной период для анализа
    time_period = datetime.now() - timedelta(days=7)
    securities = Security.objects.all()

    fall_leaders = []
    for security in securities:
        # Находим начальную цену
        start_data = Data.objects.filter(security=security, date_time__gte=time_period).order_by('date_time').first()
        # Находим конечную цену
        end_data = Data.objects.filter(security=security, date_time__gte=time_period).order_by('-date_time').first()

        # Проверяем, что есть данные для обеих дат
        if start_data and end_data:
            start_price = start_data.price
            end_price = end_data.price
            # Вычисляем процент изменения
            change = ((end_price - start_price) / start_price) * 100
            fall_leaders.append({
                'ticker': security.ticker,
                'start_price': start_price,
                'end_price': end_price,
                'change': change
            })

    # Сортируем по убыванию и отбираем топ-10
    fall_leaders = sorted(fall_leaders, key=lambda x: x['change'])[:10]
    return fall_leaders
