from django.db import models
from django.contrib.auth.models import User
import os
from django.dispatch import receiver

class Post(models.Model):
    user = models.ForeignKey(User, default = None, null = True, on_delete = models.CASCADE, related_name = 'post', verbose_name = 'Опубликовал')
    title = models.CharField(max_length = 1000, default = '', verbose_name = 'Заголовок', db_index = True)
    description = models.TextField(max_length = 3000, default = '', verbose_name = 'Содержание')
    published_at = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата создания', db_index = True)

    def __str__(self):
        return f'{self.published_at}: {self.title}'

    class Meta:
        db_table = 'posts'
        ordering = ['-published_at']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

def get_upload_path(instance, filename):
    return os.path.join('blog', instance.post.user.username, f'{instance.post.id}', filename)

class File(models.Model):
    file = models.ImageField(default = None, upload_to = get_upload_path, verbose_name = 'Файл')
    post = models.ForeignKey('Post', default = None, null = True, on_delete = models.CASCADE, related_name = 'files', verbose_name = 'Запись')
    on_delete = models.BooleanField(default = False)

    def __str__(self):
        return f'{self.file.name}'

    class Meta:
        db_table = 'files'
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'

@receiver(models.signals.post_delete, sender = File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

def get_avatar_path(instance, filename):
    return os.path.join(instance.user.username, 'avatar', filename)

class Profile(models.Model):
    user = models.OneToOneField(User, default = None, null = True, on_delete = models.CASCADE, related_name = 'profile', verbose_name = 'Пользователь')
    phone = models.CharField(max_length = 30, default = '', verbose_name = 'Телефон', blank=True)
    city = models.CharField(max_length = 30, default = '', verbose_name = 'Город', blank=True)
    photo = models.ImageField(default = None, upload_to = get_avatar_path, verbose_name = 'Аватар', blank=True)
    description = models.TextField(max_length = 3000, default = '', verbose_name = 'О себе', blank=True)
    
    def __str__(self):
        return f'Профиль: {self.user.username}'

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

@receiver(models.signals.pre_save, sender = Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    try:
        old_file = Profile.objects.get(id = instance.id).photo
    except Profile.DoesNotExist:
        return False

    new_file = instance.photo
    if old_file and new_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

@receiver(models.signals.post_delete, sender = Profile)
def auto_delete_avatar_on_delete(sender, instance, **kwargs):
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)