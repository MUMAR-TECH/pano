from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'price', 'location', 'image']  # Adjust fields as necessary

    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Property Title'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Property Description'})
        self.fields['price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Price'})
        self.fields['location'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Location'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})