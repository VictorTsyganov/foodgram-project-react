from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def create_shopping_list(user, ingredients):
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


def post_func(serializer, **kwargs):
    serializer.is_valid(raise_exception=True)
    serializer.save(**kwargs)
    return Response(
        serializer.data, status=status.HTTP_201_CREATED)


def delete_func(serializer, сlass_obj, **kwargs):
    serializer.is_valid(raise_exception=True)
    obj_for_del = get_object_or_404(сlass_obj, **kwargs)
    obj_for_del.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
