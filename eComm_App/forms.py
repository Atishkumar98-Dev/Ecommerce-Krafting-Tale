from django.forms import ModelForm, fields
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import *
from django import forms
from .models import Delivery

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Upload Excel File')


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="All Categories", required=False,
        widget=forms.Select(attrs={'class': 'form-select'}))
    search_query = forms.CharField(label="Search", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','password1','password2']

        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['shipping_address']


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['address', 'status', 'notes']
