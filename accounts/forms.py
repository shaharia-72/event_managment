from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Participant, Organizer

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class ParticipantRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name', 'aria-label': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'aria-label': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email', 'aria-label': 'Email'}))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'aria-label': 'Profile Image'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'profile_image']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email


class OrganizerRegistrationForm(UserCreationForm):
    organization_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Organization Name', 'aria-label': 'Organization Name'}))
    location = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Location', 'aria-label': 'Location'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description', 'aria-label': 'Description'}), max_length=1000, required=True)
    organization_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'aria-label': 'Organization Image'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email', 'aria-label': 'Email'}))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'Website (Optional)', 'aria-label': 'Website'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'organization_name', 'email', 'location', 'password1', 'password2', 'description', 'organization_image', 'website']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email


class ParticipantProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = Participant
        fields = ['first_name', 'last_name', 'email', 'profile_image']

class OrganizerProfileUpdateForm(forms.ModelForm):
    organization_name = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea, max_length=1000)
    organization_image = forms.ImageField(required=False)
    website = forms.URLField(required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = Organizer
        fields = [
            'email', 'organization_name', 'location', 'description', 'organization_image', 'website'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = self.instance.user.email
