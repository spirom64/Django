# Generated by Django 2.2 on 2021-01-11 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20210111_1620'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'verbose_name': 'Файл', 'verbose_name_plural': 'Файлы'},
        ),
        migrations.AlterModelTable(
            name='file',
            table='files',
        ),
    ]