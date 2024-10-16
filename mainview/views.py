from django.shortcuts import render
from django.http import JsonResponse
from moex_iss_api.get_news import get_news
from moex_iss_api.get_events import get_events
from moex_iss_api.market_data_header import get_leaders_falling, get_leaders_rising, process_securities
from moex_iss_api import get_all_securities, take_data_frame
from django.core.cache import cache
from mainview.models import Security

#Страница со списком новостей
async def news_summary(request):
    news_list = await get_news()

    context = {
        'news_list': news_list
    }
    
    return render(request, 'mainview/news_summary.html', context)

#Страница со списком мероприятий
async def events_summary(request):
    events_list = await get_events()

    context = {
        'events_list': events_list
    }

    return render(request, 'mainview/events_summary.html', context)

def homepageview(request):
    return render(request, 'mainview/mainview.html')

# Страница со списком акций
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

# Асинхронное представление для лидеров роста
async def growth_leaders_view(request):
    growth_leaders = await get_leaders_rising()  # Асинхронный вызов функции
    context = {'growth_leaders': growth_leaders}
    return render(request, 'mainview/growth_leaders.html', context)

# Асинхронное представление для лидеров падений
async def fall_leaders_view(request):
    fall_leaders = await get_leaders_falling()  # Асинхронный вызов функции
    context = {'fall_leaders': fall_leaders}
    return render(request, 'mainview/fall_leaders.html', context)