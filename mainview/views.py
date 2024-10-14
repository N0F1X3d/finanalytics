import requests
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.http import JsonResponse
from moex_iss_api import get_all_securities, take_data_frame
from django.core.cache import cache
from models import Security

def events_summary(request):
    url = 'https://iss.moex.com/iss/events.json'
    response = requests.get(url)

    events_list = []
    if response.status_code == 200:
        data = response.json()
        for item in data['events']['data']:
            events_list.append(
                {
                'title': item[2][0:60] + '...',
                'source': f'https://www.moex.com/e{item[0]}',
                'from': item[-2],
                'till': item[-1],
                }
            )
    else:
        print(f"Ошибка: {response.status_code}")
    
    context = {
        'events_list': events_list
    }

    return render(request, 'mainview/events_summary.html', context)

def news_summary(request):
    url = 'https://iss.moex.com/iss/sitenews.json'
    response = requests.get(url)

    news_list = []
    if response.status_code == 200:
        data = response.json()
        for item in data["sitenews"]["data"]:
            news_list.append({
                'title': item[2][0:60] + '...',
                'source': f'https://www.moex.com/n{item[0]}',
                'published_at': item[-1]
            })
    else:
        print(f"Ошибка: {response.status_code}")

    context = {
        'news_list': news_list
    }
    
    return render(request, 'mainview/news_summary.html', context)

def homepageview(request):
    return render(request, 'mainview/mainview.html')

# Страница со списком акций
# def securities_page(request):
#     securities_list = get_all_securities.get_securities_list()
#     return render(request, 'mainview/securities.html', {'securities': securities_list})

def securities_page(request):
    # Проверяем кэш на наличие данных
    securities_list = cache.get('securities_list')

    if not securities_list:
        # Если кэш пуст, получаем данные из API и сохраняем в кэш
        securities_list = get_all_securities.get_securities_list()
        cache.set('securities_list', securities_list, timeout=60 * 15)  # Кэшируем на 15 минут

    return render(request, 'mainview/securities.html', {'securities': securities_list})

# Обработчик запросов на получение данных о ценных бумагах
def get_securities(request, security_type):
    if security_type not in ['shares', 'bonds']:
        return JsonResponse({'error': 'Invalid security type'}, status=400)

    # Получаем данные из базы данных
    filtered_securities = Security.objects.filter(MARKET=security_type).values('SECID', 'SHORTNAME', 'BOARDID')
    
    return JsonResponse(list(filtered_securities), safe=False)

def securitie_price_chart(request, ticker):
    script, div = take_data_frame.get_script_div(ticker)
    return render(request, 'moex_iss_api/securitie_price.html', {'script':script, 'div':div, 'ticker':ticker})

def search_securities(request):
    query = request.GET.get('query', '')
    if query:
        securities_list = get_all_securities.get_securities_list()
        filtered_securities = [sec for sec in securities_list if query.lower() in sec['SHORTNAME'].lower()]
        return JsonResponse(filtered_securities, safe=False)
    return JsonResponse([], safe=False)
