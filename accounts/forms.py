"""
accounts/forms.py - Django forms for user management
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from accounts.models import UserProfile, Address


class UserRegistrationForm(UserCreationForm):
    """Form for creating a new user account."""
    email = forms.EmailField(
        label=_('Email address'),
        max_length=254,
        help_text=_('Required. Enter a valid email address.')
    )
    first_name = forms.CharField(label=_('First name'), max_length=30)
    last_name = forms.CharField(label=_('Last name'), max_length=30)

    class Meta:
        model = UserProfile
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email address is already in use.'))
        return email.lower()


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'bio', 'avatar')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError(_('Enter a valid phone number.'))
        return phone


class AddressForm(forms.ModelForm):
    """Form for creating/updating addresses."""
    class Meta:
        model = Address
        fields = (
            'address_type', 'street_address', 'apartment',
            'city', 'state', 'country', 'zip_code', 'is_default'
        )

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if zip_code and not zip_code.replace('-', '').isdigit():
            raise forms.ValidationError(_('Enter a valid ZIP/postal code.'))
        return zip_code


class PasswordChangeForm(forms.Form):
    """Form for changing user password."""
    old_password = forms.CharField(
        label=_('Current password'),
        widget=forms.PasswordInput
    )
    new_password = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput,
        min_length=8
    )
    confirm_password = forms.CharField(
        label=_('Confirm new password'),
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super(PasswordChangeForm, self).clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError(_('New passwords do not match.'))
        return cleaned_data
