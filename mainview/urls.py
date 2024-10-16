from django.urls import path
from mainview import views 

urlpatterns = [
    path('', views.homepageview, name='Главная'),
    path('securities/', views.securities_page, name='Securities'),
    path('search_securities/', views.search_securities, name='SearchSecurities'),
    path('securities_price/<str:ticker>/', views.securitie_price_chart, name='SecuritiesPriceChart'),
    path('news/', views.news_summary, name='NewsSummary'),
    path('events/', views.events_summary, name='EventsSummary'),
    path('growth-leaders/', views.growth_leaders_view, name='GrowthLeaders'),
    path('fall-leaders/', views.fall_leaders_view, name='FallLeaders'),
]
