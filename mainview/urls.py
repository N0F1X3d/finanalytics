from django.urls import path
from mainview import views 

urlpatterns = [
    path('', views.homepageview, name='Главная'),
    path('securities/', views.securities_page, name='Securities')
]
