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
    
# bookings/forms.py - Add PaymentForm
class PaymentForm(forms.Form):
    PAYMENT_METHODS = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={'class': 'form-radio'})
    )
    card_number = forms.CharField(max_length=19, required=False, widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456'}))
    expiry_date = forms.CharField(max_length=7, required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/YYYY'}))
    cvv = forms.CharField(max_length=4, required=False, widget=forms.TextInput(attrs={'placeholder': '123'}))
    name_on_card = forms.CharField(max_length=100, required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method in ['credit_card', 'debit_card']:
            if not cleaned_data.get('card_number'):
                raise ValidationError('Card number is required for card payments.')
            if not cleaned_data.get('expiry_date'):
                raise ValidationError('Expiry date is required for card payments.')
            if not cleaned_data.get('cvv'):
                raise ValidationError('CVV is required for card payments.')
            if not cleaned_data.get('name_on_card'):
                raise ValidationError('Name on card is required for card payments.')
        
        return cleaned_data