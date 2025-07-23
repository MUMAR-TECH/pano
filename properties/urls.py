from django.urls import path
from . import views

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property_list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('add/', views.PropertyCreateView.as_view(), name='add_property'),
    path('<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='edit_property'),
    path('<int:property_pk>/add-room/', views.add_room, name='add_room'),
    path('<int:property_pk>/add-review/', views.add_review, name='add_review'),
    path('vendor/properties/', views.VendorPropertyListView.as_view(), name='vendor_properties'),
    path('vendor/property/<int:pk>/', views.vendor_property_detail, name='vendor_property_detail'),

    path('vendor/properties/', views.VendorPropertyListView.as_view(), name='vendor_properties'),
    path('vendor/property/<int:pk>/', views.vendor_property_detail, name='vendor_property_detail'),
]