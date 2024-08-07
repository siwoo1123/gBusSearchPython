from django.urls import path, include
from info import views

urlpatterns = [
    path('', views.index),
    path('index/', views.index),
    path('search/', views.search),
    path('bus/', views.bus),
    path('stop/', views.stop)
]
