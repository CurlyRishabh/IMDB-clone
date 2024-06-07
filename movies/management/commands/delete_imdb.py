from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Actor, Director, Movie


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Deleting all entry....")
        with transaction.atomic():
            Movie.objects.all().delete()
            Actor.objects.all().delete()
            Director.objects.all().delete()
        print("Deleting done.")
