from django.contrib import admin

from .models import Subscriptions, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_editable = ('first_name', 'last_name', 'email')
    search_fields = ('email', 'first_name',)
    list_filter = ('email', 'first_name',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions)
