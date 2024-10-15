import httpx

async def get_events():
    url = 'https://iss.moex.com/iss/events.json'
    events_list = []

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data['events']['data']:
                events_list.append({
                    'title': item[2][0:60] + '...',  # Обрезаем заголовок
                    'source': f'https://www.moex.com/e{item[0]}',
                    'from': item[-2],
                    'till': item[-1],
                })
        else:
            print(f"Ошибка: {response.status_code}")
    
    return events_list