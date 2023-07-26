from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingList, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_favorites')
    readonly_fields = ('count_favorites',)
    list_filter = ('name', 'author__username', 'tags__name')
    search_fields = ('name', 'author__first_name',
                     'author__last_name',
                     'author__username', 'tags__name')
    empty_value_display = '-пусто-'

    def count_favorites(self, obj):
        return obj.in_favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name', 'measurement_unit',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
