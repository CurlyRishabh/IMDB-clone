from django.contrib import admin
from .models import Actor, Director, Movie, MovieRating

# Register your models here.
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Movie)
admin.site.register(MovieRating)
