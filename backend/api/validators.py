from django.core.exceptions import ValidationError

from recipes.models import Ingredient, Tag


def tags_validator(value):
    if not value:
        raise ValidationError('Не указаны тэги')
    for item in value:
        if not Tag.objects.filter(id=item):
            raise ValidationError('Указан несуществующий тэг')
    return Tag.objects.filter(id__in=value)


def ingredients_validator(value):
    if not value:
        raise ValidationError('Не указаны ингридиенты')
    ingredient_list = {}
    for item in value:
        if not Ingredient.objects.filter(pk=item['id']):
            raise ValidationError('Указан несуществующий ингидиент')
        ing_obj = Ingredient.objects.get(pk=item['id'])
        ingredient_list[item['id']] = (ing_obj, item['amount'])
    return ingredient_list
