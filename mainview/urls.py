from django.urls import path
from mainview import views

urlpatterns = [
    path('', views.homepageview, name='Главная'),
]