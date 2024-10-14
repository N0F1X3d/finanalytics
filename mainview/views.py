import requests
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.http import JsonResponse
from moex_iss_api import get_all_securities, take_data_frame

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
def securities_page(request):
    securities_list = get_all_securities.get_securities_list()
    return render(request, 'mainview/securities.html', {'securities': securities_list})

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
