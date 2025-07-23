from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'check_in_date', 'check_out_date', 'guests', 
            'guest_name', 'guest_email', 'guest_phone', 'special_requests'
        ]
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError('Check-out date must be after check-in date.')
            
            if check_in < timezone.now().date():
                raise ValidationError('Check-in date cannot be in the past.')
        
        return cleaned_data

class AvailabilityForm(forms.Form):
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()})
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError('Check-out date must be after check-in date.')
            
            if check_in < timezone.now().date():
                raise ValidationError('Check-in date cannot be in the past.')
        
        return cleaned_data