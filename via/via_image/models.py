from django.db import models
from via_superadmin.models import Company
from via_manager.models import ImageBatch

# Create your models here.

class Image(models.Model):
    filename = models.CharField(max_length=200,unique=True, blank = True)
    #will be uploaded to MEDIA_ROOT/images
    image = models.ImageField(upload_to="images/%Y%m%d/")
    width = models.IntegerField(default=1280)
    height = models.IntegerField(default=720)
    annotated = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = self.image.name
        if not self.width:
            self.width = self.image.width
        if not self.height:
            self.height = self.image.height
        super(Image, self).save(*args, **kwargs)

    class Meta:
        db_table = "images"


    
    
class LabelName(models.Model):
    name = models.CharField(max_length=100, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "labelname"


class Segment(models.Model):
    image = models.ForeignKey(ImageBatch, on_delete=models.CASCADE,)
    label = models.ForeignKey('LabelName', on_delete=models.CASCADE,)
    coords = models.TextField() ##storing list of points as string of x1,y1,x2,y2,etc.
    num_vertices = models.IntegerField()

    def __unicode__(self):
        return self.image.filename.split('.')[0] + '_' + self.label.name

    def save(self, *args, **kwargs):
        if not self.num_vertices:
            self.num_vertices = len(self.coords.split(',')) // 2
        super(Segment, self).save(*args, **kwargs)

    class Meta:
        db_table = "segment"



