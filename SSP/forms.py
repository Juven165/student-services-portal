from django import forms
from .models import DocumentApplication, Profile, DocumentType, Review


class DocumentApplicationForm(forms.ModelForm):
    class Meta:
        model = DocumentApplication
        fields = ['full_name', 'email', 'letter', 'message']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['prof_picture', 'full_name', 'email', 'mobile_number', 'address', 'message' ,]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'message']
