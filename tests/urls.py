from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('about/', views.about),
    path('data.json', views.data_json),
    path('feed/', views.feed),
    path('binary/', views.binary),
    path('fails/', views.fails),
]
