from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.forms import ModelForm
from via_superadmin.models import Company
# Create your models here.

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    video = models.FileField(upload_to='videos', blank='True', null='True')
    frames = models.FileField(upload_to='zip', blank='True', null='True')
    xml = models.FileField(upload_to='xml', blank='True', null='True')
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "video"

