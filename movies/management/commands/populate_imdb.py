from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Actor, Director, Movie
import csv as csv_module


class Command(BaseCommand):
    def import_csv(self, filename):
        print("Populating database from CSV...")

        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv_module.DictReader(file)
            i = 0
            with transaction.atomic():  # Ensuring atomic transactions
                for row in reader:
                    # Extracting movie details
                    title = row['Title']
                    release_year = int(row['Year'])
                    genre = row['Genre']
                    description = row['Description']
                    average_rating = float(row['Rating']) if row['Rating'] else 0
                    duration = int(row['Duration (min)']) if row['Duration (min)'] else 0
                    poster_url = row['Poster']
                    
                    # Create or get the movie
                    movie, created = Movie.objects.get_or_create(
                        title=title,
                        release_year=release_year,
                        genre=genre,
                        description=description,
                        average_rating=average_rating,
                        duration=duration,
                        poster_url=poster_url
                    )
                    
                    # Handling actors
                    actor_names = row['Cast'].split(', ')
                    for actor_name in actor_names:
                        actor, created = Actor.objects.get_or_create(name=actor_name)
                        movie.actors.add(actor)  # Adding actor to the movie
                    
                    # Handling directors
                    director_names = row['Director'].split(', ')
                    for director_name in director_names:
                        director, created = Director.objects.get_or_create(name=director_name)
                        movie.directors.add(director)  # Adding director to the movie

                    # Save the movie to apply the changes
                    movie.save()
                    i += 1
                    if i == 100:
                        break

        print("Database population complete.")

    def handle(self, *args, **options):
        # Assuming the CSV is named 'dataset.csv' and is located in the same directory as this script
        self.import_csv('imdb-movies-dataset.csv')
