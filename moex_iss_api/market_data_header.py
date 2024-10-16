import httpx

async def get_market_data():
    base_url = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json'
    
    params = {
        'iss.meta': 'off',  # Убираем метаданные
        'sort_column': 'VALUE',  # Сортируем по объему торгов
        'sort_order': 'desc',
        'limit': 10  # Ограничиваем количество записей
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        return None


async def get_leaders_rising():
    base_url = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json?sort_order=desc&sort_column=LASTTOPREVPRICE&limit=10'
    params = {
        'iss.meta': 'off',
        'sort_column': 'LASTTOPREVPRICE',  # Сортировка по изменению цены
        'sort_order': 'desc',
        'limit': 10  # Получаем топ 10 лидеров
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    

async def get_leaders_falling():
    base_url = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json?sort_order=asc&sort_column=LASTTOPREVPRICE&limit=10'
    params = {
        'iss.meta': 'off',
        'sort_column': 'LASTTOPREVPRICE',  # Сортировка по изменению цены
        'sort_order': 'asc',
        'limit': 10  # Получаем топ 10 лидеров
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        if response.status_code == 200:
            return response.json()
        return None

def process_securities(data):
    securities_list = []
    if data:
        for item in data['securities']['data']:
            securities_list.append({
                'secid': item[0],  # Тикер акции
                'shortname': item[2],  # Название акции
                'last_price': item[10],  # Последняя цена
                'change_percent': item[12]  # Изменение в процентах
            })
    return securities_list



    
