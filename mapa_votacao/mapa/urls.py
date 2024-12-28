
from django.urls import path
from .views import atualizar_mapa

urlpatterns = [
    path('', atualizar_mapa, name='atualizar_mapa'),
]