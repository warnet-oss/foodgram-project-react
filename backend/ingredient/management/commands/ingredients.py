import csv
import os
from foodgram import settings

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


def ingredient_create(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1]
    )


class Command(BaseCommand):

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'ingredients.csv')
        with open(path, 'r', encoding='utf-8') as file:
            row_count = sum(1 for row in file)
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                ingredient_create(row)
