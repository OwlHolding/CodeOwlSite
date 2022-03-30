from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import datetime

class UserUpgrade(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    counter = models.IntegerField(default=20)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Расширение пользователя'
        verbose_name_plural = 'Расширения пользователя'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserUpgrade.objects.create(user=instance, token=uuid.uuid4().hex)


class BlockedList(models.Model):
    name = models.CharField(max_length=255)
    ips = models.TextField(help_text="Вводите IP-адреса через пробел без запятых")

    class Meta:
        verbose_name = 'Список заблокированных IP-адресов'
        verbose_name_plural = 'Списки заблокированных IP-адресов'

    def __str__(self):
        return self.name


