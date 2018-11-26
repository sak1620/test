from via_manager.models import VideoUpload, ImageUpload
from django import forms

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoUpload
        vid_url_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
        fields = ('vid_url',)    

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        img_url_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
        fields = ('img_url',)   