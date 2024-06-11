from django.contrib import admin
from .models import Actor, Director, Movie, MovieRating, UserWatchList, MovieComment

# Register your models here.
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Movie)
admin.site.register(MovieRating)
admin.site.register(UserWatchList)
admin.site.register(MovieComment)

