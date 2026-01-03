from django.core.management.base import BaseCommand
from django.db.models import Q
from videos.models import Video
import random


class Command(BaseCommand):
    help = 'Assign random thumbnail_url to videos that lack a thumbnail or thumbnail_url'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=0, help='Limit number of videos to update (0 = all)')

    def handle(self, *args, **options):
        count = options.get('count') or 0
        # Match videos where the ImageField is empty string or NULL, and thumbnail_url is empty or NULL
        qs = Video.objects.filter(Q(thumbnail__exact='') | Q(thumbnail__isnull=True))\
              .filter(Q(thumbnail_url__exact='') | Q(thumbnail_url__isnull=True))
        total = qs.count()
        if count > 0:
            qs = qs[:count]

        updated = 0
        for v in qs:
            # Use a deterministic seed based on id for stable thumbnails, with a bit of randomness
            seed = random.randint(1, 10000)
            v.thumbnail_url = f'https://picsum.photos/seed/{v.id}-{seed}/640/360'
            v.save(update_fields=['thumbnail_url'])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f'Assigned thumbnails to {updated} videos (out of {total} candidates).'))
