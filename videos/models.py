from django.db import models
from django.contrib.auth.models import User


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    channel = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_videos', blank=True)
    # Mark short/reel style videos so UI can render them differently
    is_short = models.BooleanField(default=False)
    # Optional external URL for development/testing (e.g. public MP4) if no local file is uploaded
    external_url = models.URLField(blank=True, null=True)
    # Optional thumbnail URL (remote) when no ImageField thumbnail is provided
    thumbnail_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Threading and moderation
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_hidden = models.BooleanField(default=False)
    flagged_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Comment by {self.author} on {self.video}'


class Playlist(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title} ({self.owner.username})'


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='items')
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('playlist', 'video')

    def __str__(self):
        return f'{self.video.title} in {self.playlist.title}'


class WatchLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_later')
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f'{self.user.username} -> {self.video.title}'
from django.db import models

# Create your models here.
