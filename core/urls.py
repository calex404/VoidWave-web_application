from django.urls import path
from . import views
from .views import rebricky_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'), 
    
    path('profily/', views.profil_list_view, name='profil_list'),
    path('profily/hladat/', views.find_priatelov_view, name='find_priatelov'),
    path('profily/<int:profil_id>/', views.profil_detail_view, name='profil_detail'),
    path('profil/edit/', views.profil_edit_view, name='profil_edit'),
    
    path('accounts/register/', views.register_view, name='user_register'),
    
    path('hry/', views.hra_list_view, name='hra_list'),
    path('hry/<int:hra_id>/', views.hra_detail_view, name='hra_detail'),
    
    path('udalosti/', views.udalost_list_view, name='udalost_list'),
    path('udalosti/vytvorit/', views.udalost_create_view, name='udalost_create'),
    path('udalosti/join/<int:udalost_id>/', views.udalost_join_view, name='udalost_join'),
    path('udalosti/withdraw/<int:udalost_id>/', views.udalost_withdraw_view, name='udalost_withdraw'),
    path('udalosti/archiv/', views.udalost_archiv_view, name='udalost_archiv'),
    path('udalosti/<int:udalost_id>/hodnotit/', views.hodnotenie_create_view, name='hodnotenie_create'),
    
    path('timy/', views.tim_list_view, name='tim_list'),
    path('timy/vytvorit/', views.tim_create_view, name='tim_create'),
    path('timy/pridat-sa/<int:tim_id>/', views.tim_join_view, name='tim_join'),
    path('timy/odist/<int:tim_id>/', views.tim_leave_view, name='tim_leave'),
    
    path('oznamenia/', views.oznamenie_list_view, name='oznamenie_list'),

    path('rebricky/', rebricky_view, name='rebricek_list'),

    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('priatelstvo/send/<int:profil_id>/', views.send_friend_request, name='send_friend_request'),
    path('priatelstvo/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('priatelstvo/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),

    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/accounts/password_reset/done/'
    ), name='password_reset'),

    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/accounts/reset/done/'
    ), name='password_reset_confirm'),

    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/home.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]