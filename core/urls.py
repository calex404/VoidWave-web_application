from django.urls import path
from . import views

urlpatterns = [
    path('', views.profil_list_view, name='profil_list'),
]