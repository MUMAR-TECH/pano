from django.contrib import admin
from .models import Property, PropertyImage, Room, RoomImage, Review

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'property_type', 'city', 'owner', 'is_active', 'is_featured']
    list_filter = ['property_type', 'is_active', 'is_featured', 'city']
    search_fields = ['name', 'city', 'owner__username']
    inlines = [PropertyImageInline, RoomInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'property', 'room_type', 'price_per_night', 'capacity']
    list_filter = ['room_type', 'is_available']
    search_fields = ['name', 'property__name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['property__name', 'user__username']