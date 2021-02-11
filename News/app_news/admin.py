from django.contrib import admin
from app_news.models import News, Comments, Profile, Tags
from django.core.exceptions import PermissionDenied
from django.db.models import F

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'verification']
    actions = ['turn_verified']
    
    def turn_verified(self, request, queryset):
        if request.user.has_perm('app_news.verify_profile'):
            queryset.update(verification = True)
        else:
            raise PermissionDenied

    turn_verified.short_description = 'Перевести в статус верифицированных профилей'

class TagsInline(admin.TabularInline):
    model = Tags.news.through

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    inlines = [TagsInline]
    exclude = ['news']

class CommentsInline(admin.TabularInline):
    model = Comments

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'published_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'published_at', 'tags']
    inlines = [CommentsInline, TagsInline]
    actions = ['turn_active', 'turn_inactive', 'turn_approved']

    def turn_active(self, request, queryset):
        if request.user.has_perm('app_news.change_news'):
            queryset.update(is_active = True)
        else:
            raise PermissionDenied

    def turn_inactive(self, request, queryset):
        if request.user.has_perm('app_news.change_news'):
            queryset.update(is_active = False)
        else:
            raise PermissionDenied
    
    def turn_approved(self, request, queryset):
        if request.user.has_perm('app_news.approve_news'):
            for news in queryset:
                if not news.is_approved and news.user:
                    user = news.user
                    if hasattr(user, 'profile'):
                        user.profile.news_count = F('news_count') + 1
                        user.profile.save()
            queryset.update(is_approved = True)
        else:
            raise PermissionDenied

    turn_active.short_description = 'Перевести в статус Активна'
    turn_inactive.short_description = 'Перевести в статус Не активна'
    turn_approved.short_description = 'Одобрить'

@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'news', 'get_description']
    list_filter = ['user']
    actions = ['comment_ban']

    def get_description(self, obj):
        return f'{obj.description[:15]}...' if len(obj.description) > 15 else obj.description

    get_description.short_description = "Текст комментария"

    def comment_ban(self, request, queryset):
        if request.user.has_perm('app_news.change_comments'):
            queryset.update(description = 'Удалено администратором')
        else:
            raise PermissionDenied

    comment_ban.short_description = 'Забанить'
