from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from users.models import Subscriptions, User


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context['request']
        user = request.user
        if not request or user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user,
                                            author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredient_set', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('is_favorite', 'is_shopping_cart')

    def get_is_favorited(self, recipe):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.favorite_user.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.shopping_list_user.filter(recipe=recipe).exists()


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = CreateRecipeIngredientSerializer(
        many=True, source='recipeingredient_set')

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        ingredients_list = []
        for item in value:
            if item['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Нельзя указывать один ингредиент несколько раз')
            if item['amount'] <= 0:
                raise serializers.ValidationError(
                    'Не верно указано количество')
        return value

    def ingredients_bulk_create(self, recipe, ingredients):
        ing_objs = []
        for item in ingredients:
            id = item.get('id')
            amount = item.get('amount')
            ingredient = get_object_or_404(Ingredient, id=id)
            ing_objs.append(
                RecipeIngredient(
                    recipe=recipe, ingredient=ingredient, amount=amount
                )
            )
        return RecipeIngredient.objects.bulk_create(ing_objs)

    def create(self, validated_data):
        request = self.context['request']
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        validated_data['author'] = request.user
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.ingredients_bulk_create(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        super().update(instance, validated_data)

        if tags:
            instance.tags.set(tags)

        if ingredients:
            instance.ingredients.clear()
            self.ingredients_bulk_create(instance, ingredients)

        instance.save()
        return instance

    def to_representation(self, value):
        request = self.context['request']
        return RecipeSerializer(
            value,
            context={'request': request}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'


class SubscriptionsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = ShortRecipeSerializer(
        source='author.recipes', read_only=True, many=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='author.recipes.count',
        read_only=True
    )

    class Meta:
        model = Subscriptions
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def validate(self, data):
        request = self.context['request']
        user = request.user
        author_id = request.data['id']
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            if user == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя')
            if author.subscribing.filter(user=user).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого автора')
        if request.method == 'DELETE':
            if not author.subscribing.filter(user=user).exists():
                raise serializers.ValidationError(
                    'Вы не были подписаны на этого автора')
        return data

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated or not obj:
            return False
        return True


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    image = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        request = self.context['request']
        user = request.user
        recipe_id = request.data['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if request.method == 'POST':
            if recipe.in_favorite.filter(user=user).exists():
                raise serializers.ValidationError(
                    'Рецепт уже есть в избранном')
        if request.method == 'DELETE':
            if not recipe.in_favorite.filter(user=user).exists():
                raise serializers.ValidationError(
                    'Рецепта нет в избранном')
        return data

    def get_image(self, obj):
        request = self.context['request']
        image_url = obj.recipe.image.url
        return request.build_absolute_uri(image_url)


class ShoppingListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    image = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        request = self.context['request']
        user = request.user
        recipe_id = request.data['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if request.method == 'POST':
            if recipe.in_shopping_list.filter(user=user).exists():
                raise serializers.ValidationError(
                    'Рецепт уже есть в списке покупок'
                )
        if request.method == 'DELETE':
            if not recipe.in_shopping_list.filter(user=user).exists():
                raise serializers.ValidationError(
                    'Рецепта нет в списке покупок'
                )
        return data

    def get_image(self, obj):
        request = self.context['request']
        image_url = obj.recipe.image.url
        return request.build_absolute_uri(image_url)
