from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from videos.models import Video
import random


class Command(BaseCommand):
    help = 'Seed database with sample users and videos (no media files)'

    def handle(self, *args, **options):
        if not User.objects.filter(username='alice').exists():
            alice = User.objects.create_user('alice', password='password')
            bob = User.objects.create_user('bob', password='password')
        else:
            alice = User.objects.get(username='alice')

        titles = [
            'My first upload',
            'Funny compilation',
            'Cooking with Django',
            'Exploring the city',
        ]
        for t in titles:
            if not Video.objects.filter(title=t).exists():
                # Use public sample video + thumbnail for development so playback works without local media
                v = Video.objects.create(
                    title=t,
                    description='Sample video created by seed command',
                    channel=alice,
                    views=random.randint(0, 2000),
                    external_url='https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4',
                    thumbnail_url='https://picsum.photos/320/180?random=%d' % random.randint(1,9999),
                )
        self.stdout.write(self.style.SUCCESS('Seeded sample users and videos (without media files).'))
