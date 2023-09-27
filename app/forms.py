from django import forms
from django.db import models  
from django.forms import fields  
from .models import UploadedImage

class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ('image',)