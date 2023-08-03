from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'first_name', 'last_name', 'email')
    list_editable = ('username', 'first_name', 'last_name', 'email')
    search_fields = ('email', 'username', 'first_name')
    list_filter = ('email', 'username', 'first_name')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
