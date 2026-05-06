from django import forms
from django.contrib.auth.models import User
from SSP.models import DocumentType

class DocumentForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ['title', 'description', 'image']
