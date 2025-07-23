from django import forms
from .models import Property, Room, Review

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'name', 'property_type', 'description', 'address', 'city', 
            'state', 'country', 'postal_code', 'phone', 'email', 'website',
            'wifi', 'parking', 'restaurant', 'gym', 'pool', 'spa', 'pets_allowed'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_type', 'name', 'description', 'price_per_night', 
            'capacity', 'total_rooms', 'air_conditioning', 'balcony', 
            'tv', 'mini_bar', 'room_service'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)])
        }