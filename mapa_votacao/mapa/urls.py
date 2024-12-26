
from django.urls import path
from . import views

urlpatterns = [
    path('', views.mapa_view, name='mapa_view'),
]
