from .settings import DEBUG
from channels.models import Channel, Subscription


def sidebar_subscriptions(request):
    """Provide a small list of subscriptions or popular channels for the sidebar."""
    if request.user.is_authenticated:
        # channels this user subscribes to (limit 8)
        channels = Channel.objects.filter(subscribers__subscriber=request.user).select_related('user')[:8]
    else:
        # fallback: show recent/popular channels
        channels = Channel.objects.all().select_related('user')[:8]
    return {'sidebar_subscriptions': channels}
