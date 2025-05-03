from django import forms
from .models import DocumentImage

class DocumentImageForm(forms.ModelForm):
    class Meta:
        model = DocumentImage
        fields = ['image']