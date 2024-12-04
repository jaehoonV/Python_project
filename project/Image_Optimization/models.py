from django.db import models

class Image(models.Model):
    original_image = models.ImageField(upload_to='originals/')
    optimized_image = models.ImageField(upload_to='optimized/', blank=True, null=True)
    upload_time = models.DateTimeField(auto_now_add=True)
