from django import forms
from .models import Video


class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'placeholder':'Add a public comment...'}), max_length=1000)


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'file', 'thumbnail', 'is_short', 'external_url', 'thumbnail_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
