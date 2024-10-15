import httpx

async def get_news():
    url = 'https://iss.moex.com/iss/sitenews.json'
    news_list = []

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data["sitenews"]["data"]:
                news_list.append({
                    'title': item[2][0:60] + '...',  # Обрезаем заголовок
                    'source': f'https://www.moex.com/n{item[0]}',
                    'published_at': item[-1]
                })
        else:
            print(f"Ошибка: {response.status_code}")
    
    return news_list


