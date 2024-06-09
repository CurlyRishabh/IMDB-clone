from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from .models import Actor, Director, Movie, MovieRating, UserWatchList
from django.db import transaction


# Create your views here.
def movie_list(request):
    all_movies = Movie.objects.values()
    # movies = Movie.objects.filter(actors__id=37)
    print("in movie_list")
    return render(
        request,
        'movies/movie_list.html',
        {
            'movies': all_movies,
            'users': User.objects.all().values()
        }
        )


# @login_required(login_url='/login')
def movie_detail(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    casts = movie.actors.values()
    directors = movie.directors.values()
    for cast in casts:
        print(cast)

    return render(request,
                  template_name='movies/movie_detail.html',
                  context={'movie': movie,
                           'casts': casts,
                           'directors': directors
                           })


def add_to_watchlist(request, movie_id):
    print("clicked")
    movie = get_object_or_404(Movie, id=movie_id)
    user = request.user

    if not User.objects.filter(username=user).exists():
        return JsonResponse({'status': 'user does not exist', 'message': 'Create account to add movies to watchlist.'})
    # Check if the movie is already in the user's watchlist
    if UserWatchList.objects.filter(user=user, movie=movie).exists():
        return JsonResponse({'status': 'exists', 'message': 'Movie already in watchlist.'})

    # Add the movie to the user's watchlist
    UserWatchList.objects.create(user=user, movie=movie)
    return JsonResponse({'status': 'success', 'message': 'Movie added to watchlist.'})


def profile_page(request, user_id):
    if not request.user.is_authenticated or user_id == 'None':
        messages.error(request, "Login to view watchlist page.")
        return redirect('/login')
    user_id = int(user_id)
    if request.user.id != user_id:
        messages.error(request, "You don't have permission to view others watchlist.")
        return redirect('/login')

    watchlist_info = UserWatchList.objects.select_related('movie').filter(user=user_id).values(
        'movie_id',
        'movie__title',
        'id',
        'movie__poster_url',
        'watched'
    )
    return render(request, 'watchlist/watchlist_detail.html',
                  context={'watchlist': watchlist_info})


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            messages.error(request, "User doesn't exists")
            return redirect('/register')

        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, "Invalid password")
            return redirect('/login')
        else:
            # messages.success(request, "User logged in successfully")
            login(request, user=user)
            return redirect('/')
    return render(request, 'account/login.html')


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = User.objects.filter(username=username)
        if user.exists():
            messages.error(request, "Username already exists")
            return redirect('/register')

        with transaction.atomic():
            user = User.objects.create(
                username=username,
                email=email
            )
            user.set_password(password)
            user.save()
            messages.success(request, "Profile details updated.")
            return redirect('/')
    return render(request, 'account/register.html')


def logout_page(request):
    logout(request)
    return redirect('/login')


def search_results(request):

    title_search = request.GET.get('title')
    genre_search = request.GET.get('genre')
    rating_search = request.GET.get('rating')
    director_search = request.GET.get('director')
    actor_search = request.GET.get('actor')

    print("Search Text:", title_search)
    print(genre_search)
    print(rating_search)
    print(director_search)
    print(actor_search)
    all_movies = Movie.objects.values()
    # movies = Movie.objects.filter(actors__id=37)
    print("in movie_list")
    return render(
        request,
        'search/search_result.html',
        {
            'movies': all_movies,
            'users': User.objects.all().values()
        }
        )
