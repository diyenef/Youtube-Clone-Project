from django.core.management.base import BaseCommand
from videos.models import Video


class Command(BaseCommand):
    help = 'Mark the most recent N videos as shorts (is_short=True)'

    def add_arguments(self, parser):
        parser.add_argument('count', nargs='?', type=int, default=6, help='Number of recent videos to mark')

    def handle(self, *args, **options):
        count = options['count']
        recent = Video.objects.order_by('-uploaded_at')[:count]
        ids = [v.id for v in recent]
        updated = Video.objects.filter(id__in=ids).update(is_short=True)
        self.stdout.write(self.style.SUCCESS(f'Marked {updated} videos as shorts (ids: {ids})'))
