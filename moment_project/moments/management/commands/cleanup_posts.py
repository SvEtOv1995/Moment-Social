import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from moments.models import Post

class Command(BaseCommand):
    help = 'Удаляет посты старше 1 часа'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - datetime.timedelta(hours=1)
        deleted_count, _ = Post.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(f'Удалено {deleted_count} постов.')
