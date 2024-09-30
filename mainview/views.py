from django.shortcuts import render
from moex_iss_api import get_all_securities

def homepageview(request):
    return render(request, 'mainview/mainview.html')

def securities_page(request):
    securities_list = get_all_securities.get_securities_list()
    return render(request, 'mainview/securities.html', {'securities': securities_list})
