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


def post_delete_func(request, serializer, user, object, ClassObj, flag=False):
    if request.method == 'POST':
        if serializer.is_valid():
            if flag:
                serializer.save(user=user, author=object)
            else:
                serializer.save(user=user, recipe=object)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if serializer.is_valid():
            if flag:
                obj_for_del = get_object_or_404(
                    ClassObj, author=object, user=user)
            else:
                obj_for_del = get_object_or_404(
                    ClassObj, recipe=object, user=user)
            obj_for_del.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_400_BAD_REQUEST)
