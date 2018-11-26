from .models import Video
from via_manager.models import VideoBatch
from django import forms

class VideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ('video','frames', 'xml')
        #exclude = ['user', 'frames', 'xml', 'created_date']    
        
class VideoBatchForm(forms.ModelForm):

    class Meta:
        model = VideoBatch
        xml_file_field = forms.FileField()
        fields = ('xml_file',)        