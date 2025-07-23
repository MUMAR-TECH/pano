from django.urls import path
from .views import BookingListView, BookingDetailView, CreateBookingView, UpdateBookingView, DeleteBookingView

urlpatterns = [
    path('', BookingListView.as_view(), name='booking_list'),
    path('booking/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('booking/new/', CreateBookingView.as_view(), name='create_booking'),
    path('booking/edit/<int:pk>/', UpdateBookingView.as_view(), name='update_booking'),
    path('booking/delete/<int:pk>/', DeleteBookingView.as_view(), name='delete_booking'),
]