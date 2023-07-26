from recipes.models import RecipeIngredient


def recipe_ingredients_set(recipe, ingredients):
    objs = []
    for ingredient, amount in ingredients.values():
        objs.append(
            RecipeIngredient(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        )
    RecipeIngredient.objects.bulk_create(objs)
