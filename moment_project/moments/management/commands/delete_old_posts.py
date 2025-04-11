import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from moments.models import Post

class Command(BaseCommand):
    help = 'Удаляет анонимные посты старше 1 часа и все посты старше 24 часов'

    def handle(self, *args, **kwargs):
        # Удаляем анонимные посты старше 1 часа
        anon_cutoff = timezone.now() - datetime.timedelta(hours=1)
        anon_deleted, _ = Post.objects.filter(
            Q(author__isnull=True) & 
            Q(created_at__lt=anon_cutoff)
        ).delete()
        
        # Удаляем все посты старше 24 часов
        all_cutoff = timezone.now() - datetime.timedelta(hours=24)
        all_deleted, _ = Post.objects.filter(
            created_at__lt=all_cutoff
        ).delete()
        
        self.stdout.write(
            f'Удалено {anon_deleted} анонимных постов старше 1 часа и '
            f'{all_deleted} всех постов старше 24 часов.'
        )