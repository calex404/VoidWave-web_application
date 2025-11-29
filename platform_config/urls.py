from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1. NAŠE VLASTNÉ CESTY (Musia byť prvé, aby vyhrali!)
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

    # 2. ADMIN A OSTATNÉ (Až potom)
    path('admin/', admin.site.urls),
    
    # 3. ZVYŠOK APLIKÁCIE
    path('', include('core.urls')), 
    
    # 4. ZÁLOŽNÉ SYSTÉMOVÉ URLS (Musia byť posledné!)
    path('accounts/', include('django.contrib.auth.urls')),
]