from django.db import models  
import os
from django_cleanup import cleanup

@cleanup.select
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/', blank = True)
    uploaded_at = models.DateTimeField(auto_now_add=True)