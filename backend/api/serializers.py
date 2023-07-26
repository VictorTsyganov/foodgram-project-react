from core.services import recipe_ingredients_set
from core.validators import ingredients_validator, tags_exist_validator
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import serializers
from users.models import Subscriptions, User


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta():
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('is_favorite', 'is_shopping_cart')

    def get_is_favorited(self, recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.favorite_user.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.shopping_list_user.filter(recipe=recipe).exists()

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('recipe_ingredient__amount')
        )
        return ingredients

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not tags or not ingredients:
            raise serializers.ValidationError(
                {'errors': 'Недостаточно данных.'})

        tags = tags_exist_validator(tags, Tag)
        ingredients = ingredients_validator(ingredients, Ingredient)

        data.update(
            {
                'tags': tags,
                'ingredients': ingredients,
                'author': self.context.get('request').user,
            }
        )
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients_set(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            recipe_ingredients_set(recipe, ingredients)

        recipe.save()
        return recipe


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.StringRelatedField()
    username = serializers.StringRelatedField()
    first_name = serializers.StringRelatedField()
    last_name = serializers.StringRelatedField()
    recipes = ShortRecipeSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')
        read_only_fields = fields

    def validate(self, data):
        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            author_id = self.context['request'].data['author_id']
            author = get_object_or_404(User, id=author_id)
            if user == author:
                raise serializers.ValidationError(
                    {'errors': 'Нельзя подписаться на самого себя'})
            if author.subscribing.filter(user=user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Вы уже подписаны на этого автора'})
        return data

    def get_is_subscribed(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        return Subscriptions.objects.filter(
            author=obj, user=self.context['request'].user).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id', source='recipe', read_only=True
    )
    name = serializers.SlugRelatedField(
        slug_field='name', source='recipe', read_only=True
    )
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SlugRelatedField(
        slug_field='cooking_time', source='recipe', read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context['request'].data['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if self.context['request'].method == 'POST':
            if recipe.in_favorite.filter(user=user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепт уже есть в избранном'})
        if self.context['request'].method == 'DELETE':
            if not recipe.in_favorite.filter(user=user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепта нет в избранном'})
        return data

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.recipe.image.url
        return request.build_absolute_uri(image_url)


class ShoppingListSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id', source='recipe', read_only=True
    )
    name = serializers.SlugRelatedField(
        slug_field='name', source='recipe', read_only=True
    )
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SlugRelatedField(
        slug_field='cooking_time', source='recipe', read_only=True
    )

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context['request'].data['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if self.context['request'].method == 'POST':
            if recipe.in_shopping_list.filter(user=user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепт уже есть в списке покупок'}
                )
        if self.context['request'].method == 'DELETE':
            if not recipe.in_shopping_list.filter(user=user).exists():
                raise serializers.ValidationError(
                    {'errors': 'Рецепта нет в списке покупок'}
                )
        return data

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.recipe.image.url
        return request.build_absolute_uri(image_url)
