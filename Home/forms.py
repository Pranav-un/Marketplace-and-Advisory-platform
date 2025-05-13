from django.contrib.auth.forms import UserCreationForm
from django.forms import TextInput, PasswordInput, EmailInput
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import UserData

class UserAddForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name","email","username","password1","password2"]
        
        widgets = {
            'username': TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Choose a username',
                'autocomplete': 'username'
            }),
            'first_name': TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter first name'
            }),
            'email': EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter email address'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields which can't be set in Meta
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
        
class UserDetailsForm(ModelForm):
    class Meta:
        model = UserData
        fields = ["name","house","phone","city","state"]
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'house': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'}),
            'phone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'}),
            'state': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your state'}),
        }