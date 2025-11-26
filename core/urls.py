# core/urls.py (ČISTÁ VERZIA)

from django.urls import path
from . import views

urlpatterns = [
    # 1. KOREŇ / HOME
    path('', views.home_view, name='home'), 
    
    # 2. ZOZNAM PROFILOV
    path('profily/', views.profil_list_view, name='profil_list'),
    path('profily/<int:profil_id>/', views.profil_detail_view, name='profil_detail'),
    path('profil/edit/', views.profil_edit_view, name='profil_edit'),
    # 3. Registrácia
    path('accounts/register/', views.register_view, name='user_register'),
    
    # 4. Hry
    path('hry/', views.hra_list_view, name='hra_list'),
    path('hry/<int:hra_id>/', views.hra_detail_view, name='hra_detail'),
    
    # 5. Udalosti
    path('udalosti/', views.udalost_list_view, name='udalost_list'),
    path('udalosti/vytvorit/', views.udalost_create_view, name='udalost_create'),
    path('udalosti/join/<int:udalost_id>/', views.udalost_join_view, name='udalost_join'),
    path('udalosti/withdraw/<int:udalost_id>/', views.udalost_withdraw_view, name='udalost_withdraw'),
    # 6. Tímy
    path('timy/', views.tim_list_view, name='tim_list'),
    path('timy/vytvorit/', views.tim_create_view, name='tim_create'),
    path('timy/pridat-sa/<int:tim_id>/', views.tim_join_view, name='tim_join'),
    
    # 7. Ostatné
    path('oznamenia/', views.oznamenie_list_view, name='oznamenie_list'),
    path('rebricky/', views.rebricek_list_view, name='rebricek_list'),
] 