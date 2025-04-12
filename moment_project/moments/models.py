from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.core.exceptions import ValidationError



class Post(models.Model):
    content = models.TextField(verbose_name="Подпись", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, default="Аноним")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    hashtags = models.CharField(max_length=255, blank=True, help_text="Введите хештеги через пробел, например: #fun #life")


    def is_active(self):
        """Проверка, жив ли пост"""
        return timezone.now() - self.created_at < timedelta(hours=1)

    def __str__(self):
        return f"{self.content[:30]}..."

class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    display_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Отображаемое имя'
    )
    anonymous = models.BooleanField(
        default=True,
        verbose_name='Анонимный режим'
    )
    age = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Возраст'
    )
    interests = models.TextField(
        blank=True,
        verbose_name='Интересы'
    )
    photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        verbose_name='Фото профиля'
    )
    last_seen = models.DateTimeField(
        default=now,
        verbose_name='Последний вход'
    )
    rating = models.FloatField(
        default=0.0,
        verbose_name='Рейтинг'
    )
    total_votes = models.IntegerField(
        default=0,
        verbose_name='Количество оценок'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        ordering = ['-rating']

    def __str__(self):
        if self.display_name:
            return self.display_name
        elif self.user and self.user.username:
            return self.user.username
        return "Аноним"

    def clean(self):
        if self.age is not None and self.age < 13:
            raise ValidationError({'age': 'Возраст должен быть не менее 13 лет'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('view_profile_by_username', args=[self.user.username])
    
    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.get_or_create(user=instance)
    
class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user1.username} & {self.user2.username}'
    
class ProfileRating(models.Model):
    rater = models.ForeignKey(User, on_delete=models.CASCADE)
    target = models.ForeignKey(Profile, on_delete=models.CASCADE)
    value = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1–5

    class Meta:
        unique_together = ('rater', 'target')

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()

    @property
    def unread_count(self, user):
        return self.messages.filter(sender__in=self.participants.exclude(id=user.id), is_read=False).count()

    def __str__(self):
        return f"Chat {self.id} between {', '.join([u.username for u in self.participants.all()])}"
    
    def get_other_user(self, user):
        """Get the other participant in the chat"""
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    def __str__(self):
        return f"Message from {self.sender.username} in chat {self.chat.id}"

    class Meta:
        ordering = ['timestamp']

