from django.urls import path
from . import views


urlpatterns = [
    path('', views.profil_list_view, name='profil_list'), 
    path('accounts/register/', views.register_view, name='user_register'),
    path('hry/', views.hra_list_view, name='hra_list'),
    path('hry/<int:hra_id>/', views.hra_detail_view, name='hra_detail'),
    path('udalosti/', views.udalost_list_view, name='udalost_list'),
    path('', views.profil_list_view, name='profil_list'),
]


