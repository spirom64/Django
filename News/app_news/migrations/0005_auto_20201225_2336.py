# Generated by Django 2.2 on 2020-12-25 19:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_news', '0004_auto_20201225_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='username',
            field=models.CharField(default='', max_length=100, verbose_name='Имя пользователя'),
        ),
        migrations.AlterField(
            model_name='comments',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
