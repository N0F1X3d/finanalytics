from django.urls import path
from mainview import views 

urlpatterns = [
    path('', views.homepageview, name='Главная'),
    path('securities/', views.securities_page, name='Securities'),
    path('search_securities/', views.search_securities, name='SearchSecurities'),
    path('securities_price/<str:ticker>/', views.securitie_price_chart, name='SecuritiesPriceChart')
]
