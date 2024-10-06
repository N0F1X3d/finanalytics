from django.shortcuts import render
from django.http import JsonResponse
from moex_iss_api import get_all_securities, take_data_frame

def homepageview(request):
    return render(request, 'mainview/mainview.html')

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