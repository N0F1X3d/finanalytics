import requests
from django.shortcuts import render
from moex_iss_api import get_all_securities
from bs4 import BeautifulSoup

# Функция для парсинга данных с сайта Московской биржи
def get_stock_data(ticker):
    url = f"https://www.moex.com/ru/issue.aspx?board=TQBR&code={ticker}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Поиск текущей цены акции на странице
    price_tag = soup.find('span', class_='quote__value')
    price = price_tag.text if price_tag else "Нет данных"
    
    # Поиск логотипа компании через Google (обходной вариант)
    def get_logo_from_google(query):
        google_search_url = f"https://www.google.com/search?q={query}&tbm=isch"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(google_search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        images = soup.find_all("img")
        return images[1]["src"] if images else None
    
    logo_url = get_logo_from_google(f"{ticker} logo")
    
    return {
        "ticker": ticker,
        "price": price,
        "logo_url": logo_url
    }

# Главная страница с выводом данных о Сбербанке, Газпроме и Индексе Мосбиржи
def homepageview(request):
    # Получаем данные для нескольких акций
    stocks = [
        get_stock_data("SBER"),  # Сбербанк
        get_stock_data("GAZP"),  # Газпром
        get_stock_data("IMOEX")  # Индекс Мосбиржи
    ]
    
    # Передаем данные акций в шаблон
    return render(request, 'mainview/mainview.html', {'stocks': stocks})

# def homepageview(request):
#     return render(request, 'mainview/mainview.html')

# Страница со списком акций
def securities_page(request):
    securities_list = get_all_securities.get_securities_list()
    return render(request, 'mainview/securities.html', {'securities': securities_list})

