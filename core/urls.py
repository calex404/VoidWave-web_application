# core/urls.py (ČISTÁ VERZIA)

from django.urls import path
from . import views
from .views import rebricky_view

urlpatterns = [
    # 1. KOREŇ / HOME
    path('', views.home_view, name='home'), 
    
    # 2. ZOZNAM PROFILOV
  # 1. Zoznam všetkých profilov (bez tlačidiel - len na pozeranie)
    path('profily/', views.profil_list_view, name='profil_list'),

    # 2. Hľadanie priateľov (tento istý zoznam, ale s tlačidlami "Pridať")
    # TOTO JE TEN NOVÝ RIADOK:
    path('profily/hladat/', views.find_priatelov_view, name='find_priatelov'),

    # 3. Detail konkrétneho profilu (musí byť až za 'hladat')
    path('profily/<int:profil_id>/', views.profil_detail_view, name='profil_detail'),

    # 4. Editácia vlastného profilu
    path('profil/edit/', views.profil_edit_view, name='profil_edit'),
    path('accounts/register/', views.register_view, name='user_register'),
    
    # 4. Hry
    path('hry/', views.hra_list_view, name='hra_list'),
    path('hry/<int:hra_id>/', views.hra_detail_view, name='hra_detail'),
    
    # 5. Udalosti
    path('udalosti/', views.udalost_list_view, name='udalost_list'),
    path('udalosti/vytvorit/', views.udalost_create_view, name='udalost_create'),
    path('udalosti/join/<int:udalost_id>/', views.udalost_join_view, name='udalost_join'),
    path('udalosti/withdraw/<int:udalost_id>/', views.udalost_withdraw_view, name='udalost_withdraw'),
    path('udalosti/archiv/', views.udalost_archiv_view, name='udalost_archiv'),
    path('udalosti/<int:udalost_id>/hodnotit/', views.hodnotenie_create_view, name='hodnotenie_create'),
    # 6. Tímy
    path('timy/', views.tim_list_view, name='tim_list'),
    path('timy/vytvorit/', views.tim_create_view, name='tim_create'),
    path('timy/pridat-sa/<int:tim_id>/', views.tim_join_view, name='tim_join'),
    
    # 7. Ostatné
    path('oznamenia/', views.oznamenie_list_view, name='oznamenie_list'),

    path('priatelstvo/send/<int:profil_id>/', views.send_friend_request, name='send_friend_request'),
    path('priatelstvo/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('priatelstvo/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    # ...
    path('rebricky/', rebricky_view, name='rebricek_list'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

] 