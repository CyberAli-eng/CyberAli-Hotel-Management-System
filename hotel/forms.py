from django import forms
from .models import Customer, Room

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
