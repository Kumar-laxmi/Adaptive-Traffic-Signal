from django.db import models  
from django.db.models.signals import post_delete
from .utils import file_cleanup
  
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

post_delete.connect(
    file_cleanup, sender=UploadedImage, dispatch_uid="gallery.image.file_cleanup"
)