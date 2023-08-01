import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    help = 'Удаление/запись данных из csv в базу данных.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            dest='delete_existing',
            default=False,
            help='Удаление/запись данных из csv в базу данных.',
        )

    def handle(self, *args, **options):
        if options["delete_existing"]:
            Ingredient.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('БД очищена.'))
        else:
            with open(settings.DATA_DIR / 'ingredients.csv',
                      'r', encoding='utf-8') as file:
                reader = list(csv.reader(file))
                for i in range(len(reader)):
                    try:
                        Ingredient.objects.get_or_create(
                            name=reader[i][0],
                            measurement_unit=reader[i][1]
                        )
                    except Exception as err:
                        print(
                            f'Строка {i + 1} {reader[i]} из файла'
                            f' ingredients.csv не была загружена'
                            f' в БД. Ошибка: {err}')
            print('Загрузка данных в базу завершена.')
