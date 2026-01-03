from django.core.management.base import BaseCommand
from django.conf import settings
from videos.models import Video
import os
import urllib.request


class Command(BaseCommand):
    help = 'Download external video and thumbnail URLs to local MEDIA_ROOT and attach to Video.file and Video.thumbnail'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0, help='Limit number of videos to process (0 = all)')

    def handle(self, *args, **options):
        limit = options.get('limit') or 0
        qs = Video.objects.all().order_by('id')
        total = qs.count()
        if limit > 0:
            qs = qs[:limit]

        videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        thumbs_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        os.makedirs(videos_dir, exist_ok=True)
        os.makedirs(thumbs_dir, exist_ok=True)

        updated = 0
        for v in qs:
            changed = False
            # download video file if missing. Prefer external_url; fall back to a small public sample video
            sample_video = 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4'
            if (not v.file or not v.file.name):
                video_source = v.external_url or sample_video
                try:
                    filename = f'video_{v.id}.mp4'
                    path = os.path.join(videos_dir, filename)
                    self.stdout.write(f'Downloading video for {v.id} -> {path}')
                    urllib.request.urlretrieve(video_source, path)
                    v.file.name = os.path.join('videos', filename)
                    changed = True
                except Exception as e:
                    self.stderr.write(f'Failed to download video for {v.id}: {e}')

            # download thumbnail if missing and thumbnail_url available
            if (not v.thumbnail or not v.thumbnail.name) and v.thumbnail_url:
                try:
                    filename = f'thumb_{v.id}.jpg'
                    path = os.path.join(thumbs_dir, filename)
                    self.stdout.write(f'Downloading thumb for {v.id} -> {path}')
                    urllib.request.urlretrieve(v.thumbnail_url, path)
                    v.thumbnail.name = os.path.join('thumbnails', filename)
                    changed = True
                except Exception as e:
                    self.stderr.write(f'Failed to download thumb for {v.id}: {e}')

            if changed:
                v.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} videos (out of {total}).'))
