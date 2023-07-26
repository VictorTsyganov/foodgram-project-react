from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Subscriptions, User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_editable = ('first_name', 'last_name', 'email')
    search_fields = ('email', 'first_name',)
    list_filter = ('email', 'first_name',)
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscriptions)
admin.site.unregister(Group)
