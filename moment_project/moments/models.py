from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, default="Аноним")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def is_active(self):
        """Проверка, жив ли пост"""
        return timezone.now() - self.created_at < timedelta(hours=1)

    def __str__(self):
        return f"{self.content[:30]}..."

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, blank=True)
    anonymous = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name if not self.anonymous else "Аноним"
    
    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user1.username} & {self.user2.username}'


