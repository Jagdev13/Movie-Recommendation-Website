from django import forms
from django.contrib.auth.models import User
from django.core import validators

class RegisterUser(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'placeholder': 'First name'}))

    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': 'Last Name'}))
                                                              
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                    'placeholder': 'Enter e-mail'}),
                                     help_text="We'll never share your email with anyone else.")

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': 'Enter username'}),
                               help_text="Your username should be unique.")

    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Enter password'}),
                                validators=[validators.MinLengthValidator(8)])

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Enter password'}),
                                       help_text="Confirm your password.")

    def clean(self):
        cleaned_data = super(RegisterUser, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Password mismatch.!")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']


class EditProfile(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'placeholder': 'First name'}))

    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'placeholder': 'Last Name'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Enter password'}),
                                validators=[validators.MinLengthValidator(8)])                          
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Enter password'}),
                                       help_text="Confirm your password.")

    def clean(self):
        cleaned_data = super(EditProfile, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Password mismatch.!")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password']






