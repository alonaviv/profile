import pandas
from django.core.management.base import BaseCommand

from evaluations import models
from evaluations.models import House
from profile_server.pronouns import PronounOptions


class Command(BaseCommand):
    help = "Add to evaluations models from csv file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)
        parser.add_argument('model_name', type=str)
        model_keys_help = """This is a subset of model's fields which together form the key of an object.
        Meaning, if this key is found - you just update the object. If not, you create a new one. 
        For example, for student we will list first name and last name. All the other fields can be 
        different, and will be updated in that student, instead of creating a new object."""
        parser.add_argument('model_keys', nargs='*', type=str, help=model_keys_help)

    def handle(self, *args, **options):
        model = getattr(models, options['model_name'])
        dataframe = pandas.read_csv(options['csv_file'])
        dataframe = dataframe.apply(lambda x: x.str.strip() if x.dtype == "object" else x)  # Strip whitespaces

        for _, row in dataframe.iterrows():
            if 'house' in row:
                row.house = House.objects.get(house_name=row.house)

            if 'pronoun_choice' in row:
                row.pronoun_choice = PronounOptions(row.pronoun_choice).name

            object_filter = {key: row[key] for key in model._meta.unique_together[0]}
            model.objects.update_or_create(**object_filter, defaults=row.to_dict())
