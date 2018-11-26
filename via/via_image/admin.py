from django.contrib import admin
from via_image.models import Image, LabelName, Segment

# Register your models here.
admin.site.register(Image)
admin.site.register(LabelName)
admin.site.register(Segment)