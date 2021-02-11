# Generated by Django 2.2 on 2020-12-25 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_news', '0002_auto_20201222_2201'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['-published_at'], 'verbose_name': 'Новость', 'verbose_name_plural': 'Новости'},
        ),
        migrations.AlterField(
            model_name='comments',
            name='description',
            field=models.TextField(default='', max_length=3000, verbose_name='Текст комментария'),
        ),
        migrations.AlterField(
            model_name='news',
            name='description',
            field=models.TextField(default='', max_length=3000, verbose_name='Содержание'),
        ),
        migrations.AlterField(
            model_name='news',
            name='is_active',
            field=models.BooleanField(choices=[(False, 'Не активна'), (True, 'Активна')], default=True, verbose_name='Статус'),
        ),
    ]
