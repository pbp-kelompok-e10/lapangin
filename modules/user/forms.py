from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserForm(forms.ModelForm):
    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0062FF] focus:border-transparent outline-none',
            'placeholder': 'Enter full name'
        }),
        required=False
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0062FF] focus:border-transparent outline-none',
            'placeholder': 'Enter password'
        }),
        required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0062FF] focus:border-transparent outline-none',
            'placeholder': 'Confirm password'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0062FF] focus:border-transparent outline-none',
                'placeholder': 'Enter username'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name', '').strip()
        # Split full name into first_name and last_name
        parts = full_name.split(' ', 1)
        user.first_name = parts[0] if len(parts) > 0 else ''
        user.last_name = parts[1] if len(parts) > 1 else ''
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'is_active']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0062FF] focus:border-transparent outline-none',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0062FF] focus:border-transparent outline-none',
                'placeholder': 'Enter address',
                'rows': 3
            }),
        }
