from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('create/<int:room_id>/', views.create_booking, name='create_booking'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('vendor/', views.vendor_bookings, name='vendor_bookings'),
    path('<int:pk>/confirm/', views.confirm_booking, name='confirm_booking'),
    path('availability/<int:room_id>/', views.room_availability, name='room_availability'),
    # urls.py - Add this pattern
    path('availability/check/', views.check_availability, name='check_availability'),
]