from django.db import models
from via_superadmin.models import Company
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User, Group

# Create your models here.
class Batch(models.Model):
    name = models.CharField(max_length=255, blank=False)
    path = models.CharField(max_length=500, blank=True)
    count  = models.IntegerField(null=True)
    saveId = models.CharField(max_length=255, blank=False, default=0)
    status = models.IntegerField(blank=True, default=1)
    supervisor = models.ForeignKey( User, on_delete=models.CASCADE, blank=False)
    company =  models.ForeignKey(Company, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    completeby_date = models.DateField(null=True, blank=True)
    assigned_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    batch_type = models.IntegerField(null=True)

    class Meta:
        db_table = "batch"


class VideoBatch(models.Model):
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=200)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    user = models.ForeignKey( User, on_delete=models.CASCADE, blank=False)
    status = models.IntegerField(blank=True, null=True, default=1)
    frames = models.FileField(upload_to='frames/%Y%m%d/', blank='True', null='True')
    xml = models.TextField(blank='True', null='True')
    xml_file = models.FileField(upload_to='xml/%Y%m%d/', blank='True', null='True')
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    class Meta:
        db_table = "videobatch"


class VideoUpload(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    vid_url = models.FileField(upload_to='videos/%Y%m%d/')
    status = models.IntegerField(default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    class Meta:
        db_table = "videoupload"


class ImageBatch(models.Model):
    name = models.CharField(max_length=50)
    width = models.IntegerField(default=1280)
    height = models.IntegerField(default=720)
    annotated = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    path = models.CharField(max_length=200)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(blank=True, default=1)
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    class Meta:
        db_table = "imagebatch"


class ImageUpload(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    img_url = models.FileField(upload_to='images/%Y%m%d/')
    status = models.IntegerField(default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    class Meta:
        db_table = "imageupload"


class OperatorBatchMapping(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="manager")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    class Meta:
        db_table = "operatorbatchmapping"


# class ImageUpload(models.Model):
#     name = models.CharField(max_length=255, blank=False)
#     img_url = models.FileField(upload_to='images/%Y%m%d/')
#     status = models.IntegerField(default=0)
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     created_date = models.DateTimeField(
#         default=timezone.now)
#     published_date = models.DateTimeField(
#         blank=True, null=True)

#     class Meta:
#         db_table = "imageupload"


# class OperatorBatchMapping(models.Model):
#     batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
#     operator = models.ForeignKey(User, on_delete=models.CASCADE)
#     supervisor_id = models.IntegerField(null=True)
#     company_id = models.IntegerField(null=True)
#     status = models.IntegerField(default=0)
#     created_date = models.DateTimeField(
#         default=timezone.now)
#     published_date = models.DateTimeField(
#         blank=True, null=True)

#     class Meta:
#         db_table = "operatorbatchmapping"
