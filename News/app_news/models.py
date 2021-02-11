from django.db import models
from django.contrib.auth.models import User

class News(models.Model):
    status_choices = [
        (False, 'Не активна'),
        (True, 'Активна')
    ]
    approve_choices = [
        (False, 'Не одобрена'),
        (True, 'Одобрена')
    ]
    user = models.ForeignKey(User, default = None, null = True, on_delete = models.CASCADE, related_name = 'user', verbose_name = 'Опубликовал')
    title = models.CharField(max_length = 1000, default = '', verbose_name = 'Название', db_index = True)
    description = models.TextField(max_length = 3000, default = '', verbose_name = 'Содержание')
    published_at = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата создания', db_index = True)
    updated_at = models.DateTimeField(auto_now = True, verbose_name = 'Дата редактирования')
    is_active = models.BooleanField(default = True, verbose_name = 'Статус', choices = status_choices)
    is_approved = models.BooleanField(default = False, verbose_name = 'Одобрение', choices = approve_choices)

    def __str__(self):
        return f'{self.published_at}: {self.title}'

    class Meta:
        db_table = 'news'
        ordering = ['-published_at']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        permissions = (
            ('approve_news', 'Может одобрять'),
        )

class Comments(models.Model):
    user = models.ForeignKey(User, default = None, null = True, on_delete = models.CASCADE, related_name = 'user_comments', verbose_name = 'Пользователь')
    description = models.TextField(max_length = 3000, default = '', verbose_name = 'Текст комментария')
    news = models.ForeignKey('News', default = None, null = True, on_delete = models.CASCADE, related_name = 'comments', verbose_name = 'Новость')
    username = models.CharField(max_length = 100, default = '', verbose_name = 'Имя пользователя')
    

    def __str__(self):
        if self.user:
            return f'{self.user.username}: {self.description}'
        elif hasattr(self, 'username'):
            return f'{self.username}: {self.description}'
        else:
            return f'NONAME: {self.description}'

    class Meta:
        db_table = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class Profile(models.Model):
    verification_choices = [
        (False, 'Не пройдена'),
        (True, 'Пройдена')
    ]
    user = models.OneToOneField(User, default = None, null = True, on_delete = models.CASCADE, related_name = 'profile', verbose_name = 'Пользователь')
    phone = models.CharField(max_length = 30, default = '', verbose_name = 'Телефон')
    city = models.CharField(max_length = 30, default = '', verbose_name = 'Город')
    verification = models.BooleanField(default = 'False', verbose_name = 'Верификация', choices = verification_choices)
    news_count = models.IntegerField(default = 0, verbose_name = 'Новостей опубликовано')
    

    def __str__(self):
        return f'Профиль: {self.user.username}'

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        permissions = (
            ('verify_profile', 'Может верифицировать'),
        )

class Tags(models.Model):
    tag = models.CharField(max_length = 30, default = '', verbose_name = 'Тег')
    news = models.ManyToManyField('News', default = None, verbose_name = 'Новости', related_name = 'tags')
    
    def __str__(self):
        return f'{self.tag}'

    class Meta:
        db_table = 'tags'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'