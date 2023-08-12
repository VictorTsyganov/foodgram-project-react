# Проект Foodgram

[![Python](https://img.shields.io/badge/-Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-464646?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Postman](https://img.shields.io/badge/Postman-464646?style=flat-square&logo=postman)](https://www.postman.com/)

## Описание

Проект "Foodgram" – это социальная сеть, в которой авторизированные пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. Для неавторизированных пользователей доступны просмотр рецептов и страниц авторов.

## Как запустить проект локально в контейнерах:

Клонировать репозиторий и перейти в него в командной строке (в папку infra):

``` git@github.com:VictorTsyganov/foodgram-project-react.git ``` 

``` cd foodgram-project-react/infra/ ``` 

Запустить docker-compose:

```
docker-compose up

```

После окончания сборки контейнеров выполнить миграции:

```
docker-compose exec backend python manage.py migrate

```

Загрузить статику:

```
docker-compose exec backend python manage.py collectstatic

```

Скопировать статику в вольюм:

```
docker compose exec backend cp -r /app/static_backend/. /static_backend/
```

Проверить работу проекта возможно по любой из ссылок:

```
http://localhost/

http://127.0.0.1/
```

**Документация для Foodgram будет доступна по любой из ссылок**:

```
http://localhost/api/docs/

http://127.0.0.1/api/docs/ 
```

## Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

``` git@github.com:VictorTsyganov/foodgram-project-react.git ```

``` cd foodgram-project-react ``` 

Создать и активировать виртуальное окружение:

``` python -m venv venv ``` 

* Если у вас Linux/macOS:
    ``` source venv/bin/activate ``` 

* Если у вас Windows:
    ``` source venv/Scripts/activate ```
    
``` python -m pip install --upgrade pip ``` 

Перейти в папку backend в командной строке:

``` cd backend ``` 

Установить зависимости из файла requirements:

``` pip install -r requirements.txt ``` 

В файле настроек (settings.py) изменить базу данных на sqlite3 и выполнить миграции:

``` python manage.py migrate ``` 

Запустить проект:

``` python manage.py runserver ```

Проверить работу проекта возможно по любой из ссылок с помощью программы Postman:

```
http://localhost:8000/

http://127.0.0.1:8000/
```

**Документация для Foodgram будет доступна по любой из ссылок после локального запуска контейнеров frontend и nginx**:

```
http://localhost/api/docs/

http://127.0.0.1/api/docs/ 
```

## Работа с загрузкой ингредиентов из csv файлов в базу данных.

* Для удаления имеющихся записей из базы данных, необходимо в командной строке, из дериктории, в которой находится файл manage.py, запустить команду *python manage.py uploader --delete-existing*.
* Для справки - *python manage.py uploader -h или --help*.
* Для загрузки данных из csv файлов в базу данных, необходимо в командной строке, из дериктории, в которой находится файл manage.py, запустить команду *python manage.py uploader*.
* При возникновении ошибок, данные о них будут отражены в терминале. 

## Функционал

**Рецепты**: получить список всех рецептов, создать рецепт, информация о рецепте, обновить информацию о рецепте, удалить рецепт.

**Теги**: получить список всех тегов, получить определенный тег.

**Ингредиенты**: получить список всех ингредиентов, получить определенный ингредиент.

**Список покупок**: скачать список покупок, добавить рецепт в список покупок, удалить рецепт из списка покупок.

**Подписки**: получить список всех подписок пользователя, подписаться на автора, удалить подписку.

**Избранное**: Добавить рецепт в избранное, рецепт из избранного.

**Пользователи**: получить список всех пользователей, создание пользователя, получить пользователя по id, получить текущего пользователя me, изменить пароль, получить токен авторизации, удаление токена.

## Ресурсы

```python
# Документаия проекта
http://localhost/api/docs/

http://127.0.0.1/api/docs/ 
```

```python
# ПО для тестирования API, Postman
https://www.postman.com/
```

## Системные требования
- Python 3.9+
- Works on Linux, Windows, macOS

## Стек технологий

- Python 3.9

- Django 3.2

- DRF

- Djoser

## Автор

[Виктор Цыганов](https://github.com/VictorTsyganov)
