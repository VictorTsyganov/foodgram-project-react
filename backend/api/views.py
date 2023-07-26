from api.permissions import AdminOrReadOnly, AuthorStaffOrReadOnly
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscriptions, User

from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          SubscriptionsSerializer, TagSerializer)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            User.objects.filter(subscribing__user=self.request.user)
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
        request.data['author_id'] = id
        serializer = SubscriptionsSerializer(
            data=request.data, context={'request': request})
        if request.method == 'POST' and serializer.is_valid():
            Subscriptions.objects.create(user=user, author=author)
            serializer = SubscriptionsSerializer(
                instance=author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscribe = get_object_or_404(
                Subscriptions, user=user, author=author)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None


class CustomSearchFilter(filters.SearchFilter):
    search_param = 'name'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None
    filter_backends = (CustomSearchFilter, )
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'tags', 'author'
        ).all()
        params = self.request.query_params
        if self.request.method == 'GET':
            tags = params.getlist('tags')
            if tags:
                recipes = recipes.filter(tags__slug__in=tags).distinct()
            if params.get('author'):
                author = get_object_or_404(User, id=params.get('author'))
                recipes = recipes.filter(author=author)
            if self.request.user.is_authenticated:
                if params.get('is_favorited'):
                    favorit_obj = Favorite.objects.filter(
                        user=self.request.user)
                    recipes = recipes.filter(
                        id__in=favorit_obj.values('recipe_id'))
                if params.get('is_in_shopping_cart'):
                    shopping_obj = ShoppingList.objects.filter(
                        user=self.request.user)
                    recipes = recipes.filter(
                        id__in=shopping_obj.values('recipe_id'))
        return recipes

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            request.data['id'] = recipe.id
            serializer = FavoriteSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            request.data['id'] = recipe.id
            serializer = FavoriteSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                favorite = get_object_or_404(
                    Favorite, recipe=recipe, user=user)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            request.data['id'] = recipe.id
            serializer = ShoppingListSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            request.data['id'] = recipe.id
            serializer = ShoppingListSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                favorite = get_object_or_404(
                    ShoppingList, recipe=recipe, user=user)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

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
        shopping_list = (
            f'Список покупок пользователя: {user.get_full_name()}\n\n'
        )
        for ingredient in ingredients:
            shopping_list += ''.join([
                f'- {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["amount"]}\n'
            ])
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, headers={
            'Content-Type': 'text/plain',
            'Content-Disposition': f'attachment; filename={filename}'
        })

        return response
