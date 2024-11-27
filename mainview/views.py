from django.shortcuts import render
from django.http import JsonResponse
from moex_iss_api.market_data_header import get_leaders_falling, get_leaders_rising
from moex_iss_api import take_data_frame, get_events, get_news
from django.core.cache import cache
from mainview.models import Security, Bond
from django.db.models import Q
from .forms import ChartForm
from ml.predictor import train_and_predict, generate_graph

#Главная страница
def homepageview(request):
    #take_data_frame.fill_data()
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


# Страница со списком акций и облигаций
def securities_page(request):
    security_type = request.GET.get('type')
    ticker = request.GET.get('ticker')
    min_value = request.GET.get('min_value')
    max_value = request.GET.get('max_value')
    sort_by = request.GET.get('sort_by')

    queryset = None
    filtered_securities = []
    filter_label = "Цена"  # По умолчанию для акций

    # Определяем, с каким типом ценных бумаг работаем
    if security_type:
        match security_type:
            case 'shares':
                queryset = Security.objects.all()
                filter_label = "Цена"  # Для акций используем "Цена"
            case 'bonds':
                queryset = Bond.objects.all()
                filter_label = "Доходность"  # Для облигаций используем "Доходность"

        if queryset is not None:
            # Применяем фильтры
            filters = {}
            if min_value:
                filters['current_price__gte'] = min_value
            if max_value:
                filters['current_price__lte'] = max_value
            if ticker:
                filters['ticker__icontains'] = ticker
            queryset = queryset.filter(**filters)

            # Применяем сортировку
            if sort_by:
                match sort_by:
                    case 'ticker_asc':
                        queryset = queryset.order_by('ticker')
                    case 'ticker_desc':
                        queryset = queryset.order_by('-ticker')
                    case 'price_asc':
                        queryset = queryset.order_by('current_price')
                    case 'price_desc':
                        queryset = queryset.order_by('-current_price')

            filtered_securities = queryset.values('ticker', 'name', 'current_price')

    return render(request, 'mainview/securities.html', {
        'securities': filtered_securities,
        'security_type': security_type,
        'filter_label': filter_label  # Динамическая метка для фильтра
    })


#Страница с графиком акции
def securitie_price_chart(request, ticker):
    form = ChartForm(request.POST or None, ticker=ticker)
    chart_html = None
    
    if form.is_valid():
        # Получаем данные начала и окончания из формы
        start = form.cleaned_data.get('start')
        end = form.cleaned_data.get('end')
        
        # Передаем данные в get_chart_html
        chart_html = take_data_frame.get_chart_html(ticker, start=start, end=end)
    else:
        # Инициализируем график без фильтрации дат, если форма не заполнена
        chart_html = take_data_frame.get_chart_html(ticker)
    
    return render(request, 'moex_iss_api/securitie_price.html', {'chart': chart_html, 'ticker': ticker, 'form': form})

def search_securities(request):
    query = request.GET.get('query', '')
    filtered_securities = []
    if query:
        securities = Security.objects.filter(name__icontains=query) | Security.objects.filter(ticker__icontains=query)
        filtered_securities = list(securities.values('name', 'ticker'))
    return JsonResponse({'filtered_securities': filtered_securities})

# Асинхронное представление для лидеров роста
def growth_leaders_view(request):
    growth_leaders = get_leaders_rising()
    context = {'growth_leaders': growth_leaders}
    return render(request, 'mainview/growth_leaders.html', context)

def fall_leaders_view(request):
    fall_leaders = get_leaders_falling()
    context = {'fall_leaders': fall_leaders}
    return render(request, 'mainview/fall_leaders.html', context)

def predict_prices(request, ticker):
    # Получаем объект Security для тикера
    security = Security.objects.get(ticker=ticker)

    # Обучаем модель и получаем предсказания
    real_prices, predicted_prices = train_and_predict(ticker)

    # Генерируем график
    graph_html = generate_graph(ticker, real_prices, predicted_prices)

    # Рендерим шаблон с графиком
    return render(request, 'mainview/predictions.html', {'graph': graph_html, 'ticker': ticker})