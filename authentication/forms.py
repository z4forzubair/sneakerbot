from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.instance = kwargs.pop('instance', None)
        super(SignUpForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name"
            }
        ))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name"
            }
        ))
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
