from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import BankCard, Category, Profile, Contacts
from django.forms import TextInput, Textarea, EmailInput, NumberInput, DateTimeField


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class ContactsForm(forms.ModelForm):
    class Meta:
        model = Contacts 
        fields = ["full_name","email_address", "company","phone_number","message"]
        widgets = {
                "full_name": TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': "Enter your name"
                }),
                "email_address": EmailInput(attrs={
                    'class' : 'form-control',
                    'placeholder' :  "you@email.com"
                }),
                "company": TextInput(attrs={
                    'class' : 'form-control',
                    'placeholder':  "Enter your company"
                }),
                "phone_number": NumberInput(attrs={
                    'class' : 'form-control',
                    'placeholder':  "Enter your number"
                }),
                "message": Textarea(attrs={
                    'class' : 'form-control',
                    'placeholder':  "Type here"
                }),
            }


class BankCardForm(forms.ModelForm):
    class Meta:
        model = BankCard
        fields = ('cardName', 'cardBalance')

        widgets = {
            "cardBalance": forms.TextInput(attrs={
                'class' : 'form-control',
                'placeholder' :  "Type balance of card"
            }),
            "cardName": forms.Select(
                choices = BankCard.objects.all().values_list('cardName', 'cardName'),
                attrs={
                'class' : 'form-control'
            }),
            # "date": forms.DateTimeField(attrs={
            #     'class' : 'form-control',
            #     'placeholder':  "Type date of crating"
            # }),
        }

