from django.core.management.base import BaseCommand
from django.conf import settings
from videos.models import Video
import os
import shutil
import subprocess


class Command(BaseCommand):
    help = 'Transcode existing video files to 480p using ffmpeg (writes to MEDIA_ROOT/transcoded/)'

    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing transcodes')

    def handle(self, *args, **options):
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            self.stdout.write(self.style.ERROR('ffmpeg not found in PATH. Please install ffmpeg to use this command.'))
            return

        out_dir = os.path.join(settings.MEDIA_ROOT, 'transcoded')
        os.makedirs(out_dir, exist_ok=True)

        qs = Video.objects.exclude(file='').exclude(file__isnull=True)
        total = qs.count()
        if total == 0:
            self.stdout.write('No local video files found to transcode.')
            return

        done = 0
        for v in qs:
            try:
                src = v.file.path
            except Exception:
                self.stdout.write(self.style.WARNING(f'Skipping video id={v.id}: no local file path'))
                continue

            base_out = f'video_{v.id}_480.mp4'
            out_path = os.path.join(out_dir, base_out)
            if os.path.exists(out_path) and not options['overwrite']:
                self.stdout.write(f'Skipping existing: {out_path}')
                continue

            cmd = [ffmpeg, '-y', '-i', src, '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-vf', "scale='min(854,iw)':'min(480,ih)':force_original_aspect_ratio=decrease", '-c:a', 'aac', '-b:a', '128k', out_path]
            self.stdout.write(f'Transcoding id={v.id} -> {out_path}')
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                done += 1
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(f'Failed to transcode id={v.id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Transcoding finished: {done}/{total} files processed.'))
