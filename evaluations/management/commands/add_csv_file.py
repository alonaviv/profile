from django.core.management.base import BaseCommand
from evaluations import models
from evaluations.models import House
import pandas


class Command(BaseCommand):
    help = "Add to evaluations models from csv file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)
        parser.add_argument('model_name', type=str)

    def handle(self, *args, **options):
        model = getattr(models, options['model_name'])
        dataframe = pandas.read_csv(options['csv_file'])

        for _, row in dataframe.iterrows():
            if 'house' in row:
                row.house = House.objects.get(house_name=row.house)

            model.objects.get_or_create(**row)
