from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [

    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
   
    # Password Reset URLs
    path('forgot-password/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('forgot-password/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('complete-profile/', views.complete_profile, name='complete_profile'),

    
    path('verify-host-otp/', views.verify_host_otp, name='verify_host_otp'),
    
    path('register-host/', views.register_host, name='register_host'),
    


    # profile urls
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),


    # dashboard urls
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
   
]