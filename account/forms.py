from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit role choices
        self.fields['role'].choices = [
            ('student', 'Student'),
            ('staff', 'Staff'),
        ]