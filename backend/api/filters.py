from django_filters import rest_framework as filters

from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from users.models import User


class FilterIngredient(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class FilterRecipe(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all()
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                favorit_obj = Favorite.objects.filter(user=user)
                queryset = queryset.filter(
                    id__in=favorit_obj.values('recipe_id'))
                return queryset
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                shopping_obj = ShoppingList.objects.filter(user=user)
                queryset = queryset.filter(
                    id__in=shopping_obj.values('recipe_id'))
                return queryset
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
