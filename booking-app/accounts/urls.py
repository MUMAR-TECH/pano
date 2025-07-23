from django.urls import path
from .views import (
    profile_view,
    edit_profile,
    vendor_dashboard,
    VendorSignUpView,
    login_view,
    logout_view,
    password_reset_view,
)

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('vendor-dashboard/', vendor_dashboard, name='vendor_dashboard'),
    path('signup/vendor/', VendorSignUpView.as_view(), name='vendor_signup'),
    path('login/', login_view, name='account_login'),
    path('logout/', logout_view, name='account_logout'),
    path('password-reset/', password_reset_view, name='password_reset'),
]