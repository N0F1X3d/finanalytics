from django.shortcuts import render
from django.http import JsonResponse
from moex_iss_api.get_news import get_news
from moex_iss_api.get_events import get_events
from moex_iss_api.market_data_header import get_leaders_falling, get_leaders_rising, process_securities
from moex_iss_api import get_all_securities, take_data_frame
from django.core.cache import cache
from mainview.models import Security, Bond

#Главная страница
def homepageview(request):
    return render(request, 'mainview/mainview.html')

#Страница со списком новостей
async def news_summary(request):
    news_list = await get_news.get_news()

    context = {
        'news_list': news_list
    }
    
    return render(request, 'mainview/news_summary.html', context)

#Страница со списком мероприятий
async def events_summary(request):
    events_list = await get_events.get_events()

    context = {
        'events_list': events_list
    }

    return render(request, 'mainview/events_summary.html', context)


# Страница со списком акций
def securities_page(request):
    security_type = request.GET.get('type')
    get_all_securities.get_securities_list()
    filtered_securities = []
    if security_type:
        match security_type:
            case 'shares':
                filtered_securities = Security.objects.values('ticker', 'name', 'current_price')
            case 'bonds':
                filtered_securities = Bond.objects.values('ticker', 'name', 'current_price')
            case _:
                filtered_securities = []
    return render(request, 'mainview/securities.html', {'securities': filtered_securities})


#Страница с графиком акции
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
