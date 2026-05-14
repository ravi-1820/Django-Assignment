from django import forms
from django.contrib.auth.models import User
from .models import Patient, Doctor

class UserRegistrationForm(forms.Form):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}), required=True)
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    
    # Doctor specific fields
    specialty = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialty (Doctors only)'}))
    location = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location (Doctors only)'}))

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        specialty = cleaned_data.get('specialty')
        location = cleaned_data.get('location')
        
        if role == 'doctor':
            if not specialty:
                self.add_error('specialty', 'Specialty is required for doctors.')
            if not location:
                self.add_error('location', 'Location is required for doctors.')
        
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['name']
        )
        
        role = self.cleaned_data['role']
        if role == 'patient':
            profile = Patient.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone']
            )
        else:
            profile = Doctor.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                specialty=self.cleaned_data['specialty'],
                location=self.cleaned_data['location'],
                phone=self.cleaned_data['phone'],
                availability=True
            )
        return user, profile
