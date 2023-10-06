from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from.models import Follow


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username')
    list_filter = ('email', 'username')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    list_filter = ('user', 'following')
    search_fields = ('user__username', 'following__username')
