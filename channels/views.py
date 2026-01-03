from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from videos.models import Video
from .models import Channel, Subscription


def channel_profile(request, username):
    user = get_object_or_404(User, username=username)
    # ensure channel exists
    channel, _ = Channel.objects.get_or_create(user=user, defaults={'display_name': user.username})
    videos = Video.objects.filter(channel=user).order_by('-uploaded_at')
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(subscriber=request.user, channel=channel).exists()
    return render(request, 'channels/profile.html', {'channel': channel, 'videos': videos, 'is_subscribed': is_subscribed})


@login_required
def toggle_subscribe(request, username):
    channel_user = get_object_or_404(User, username=username)
    channel = Channel.objects.get_or_create(user=channel_user)[0]
    sub, created = Subscription.objects.get_or_create(subscriber=request.user, channel=channel)
    if not created:
        sub.delete()
        created = False
    return redirect('channel_profile', username=username)
