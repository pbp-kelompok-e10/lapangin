from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from modules.user.models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    # Add your custom fields here
    full_name = forms.CharField(max_length=255, required=False, help_text='Optional.')
    phone = forms.CharField(max_length=15, required=False, help_text='Optional.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('full_name', 'phone',)

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name', '').strip()
        # Split full name into first_name and last_name
        if full_name:
            parts = full_name.split(' ', 1)
            user.first_name = parts[0] if len(parts) > 0 else ''
            user.last_name = parts[1] if len(parts) > 1 else ''
        
        if commit:
            user.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                full_name=full_name,
                phone=self.cleaned_data.get('phone', '')
            )
        return user