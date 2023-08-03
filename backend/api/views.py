from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from users.models import Subscriptions, User
from .permissions import AuthorOrStaffOrReadOnly
from .serializers import (CreateRecipeSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          SubscriptionsSerializer, TagSerializer)
from .utils import create_shopping_list, post_delete_func


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        user = self.request.user
        pages = self.paginate_queryset(
            Subscriptions.objects.filter(user=user)
        )

        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        request.data['id'] = id
        serializer = SubscriptionsSerializer(
            data=request.data, context={'request': request})
        flag = True
        return post_delete_func(
            request, serializer, user, author, Subscriptions, flag)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class FilterIngredient(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FilterIngredient
    pagination_class = None


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

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if name == 'is_favorited' and value is True:
                favorit_obj = Favorite.objects.filter(user=user)
                queryset = queryset.filter(
                    id__in=favorit_obj.values('recipe_id'))
                return queryset
        return queryset

    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if name == 'is_in_shopping_cart' and value is True:
                shopping_obj = ShoppingList.objects.filter(user=user)
                queryset = queryset.filter(
                    id__in=shopping_obj.values('recipe_id'))
                return queryset
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AuthorOrStaffOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FilterRecipe

    def get_serializer_class(self):
        if (self.request.method == 'POST'
                or self.request.method == 'PATCH'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.prefetch_related(
            'tags', 'author', 'recipeingredient_set'
        ).all()
        return queryset

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        request.data['id'] = recipe.id
        serializer = FavoriteSerializer(
            data=request.data, context={'request': request})
        return post_delete_func(
            request, serializer, user, recipe, Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        request.data['id'] = recipe.id
        serializer = ShoppingListSerializer(
            data=request.data, context={'request': request})
        return post_delete_func(
            request, serializer, user, recipe, ShoppingList)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_list_user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_list__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return create_shopping_list(user, ingredients)
