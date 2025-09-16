from django.urls import path
from . import views

app_name = 'properties'



urlpatterns = [
    path('', views.HomeView.as_view(), name='property_list'),
    path('propperties', views.PropertyListView.as_view(), name='property_list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),

    path('add/', views.PropertyCreateView.as_view(), name='add_property'),
    path('<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_update'),

    path('<int:property_pk>/add-room/', views.add_room, name='add_room'),
    path('room/<int:pk>/edit/',views.RoomUpdateView.as_view(),name='room_update'),

    path('<int:property_pk>/add-review/', views.add_review, name='add_review'),

    path('vendor/properties/', views.VendorPropertyListView.as_view(), name='vendor_properties'),
    path('vendor/property/<int:pk>/', views.vendor_property_detail, name='vendor_property_detail'),

    path('vendor/properties/', views.VendorPropertyListView.as_view(), name='vendor_properties'),
    path('vendor/property/<int:pk>/', views.vendor_property_detail, name='vendor_property_detail'),

    path('', views.HomeView.as_view(), name='home'),  # Add this line
    path('properties/', views.PropertyListView.as_view(), name='property_list'),

    # urls.py - Add this pattern
    path('availability/check/', views.check_availability, name='check_availability'),

    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
]