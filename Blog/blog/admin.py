from django.contrib import admin
from blog.models import Profile, File, Post

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'description', 'photo']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'get_description']

    def get_description(self, obj):
        return f'{obj.description[:15]}...' if len(obj.description) > 15 else obj.description

    get_description.short_description = 'Содержание'

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['post', 'file']