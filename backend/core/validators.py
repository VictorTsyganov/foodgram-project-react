from django.core.exceptions import ValidationError


def tags_exist_validator(tags, Tag):
    if not tags:
        raise ValidationError('Не указаны тэги')
    tags_db = Tag.objects.filter(id__in=tags)
    if len(tags_db) != len(tags):
        raise ValidationError('Указан несуществующий тэг')
    return tags_db


def ingredients_validator(ingredients, Ingredient):
    if not ingredients:
        raise ValidationError('Не указаны ингридиенты')
    valid_ings = {}
    for ing in ingredients:
        if not (isinstance(ing['amount'], int) or ing['amount'].isdigit()):
            raise ValidationError('Неправильное количество ингидиента')

        valid_ings[ing['id']] = int(ing['amount'])
        if valid_ings[ing['id']] <= 0:
            raise ValidationError('Неправильное количество ингридиента')

    if not valid_ings:
        raise ValidationError('Неправильные ингидиенты')

    db_ings = Ingredient.objects.filter(pk__in=valid_ings.keys())
    if not db_ings:
        raise ValidationError('Неправильные ингидиенты')

    for ing in db_ings:
        valid_ings[ing.pk] = (ing, valid_ings[ing.pk])

    return valid_ings
