import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages

from .models import MovieComment, Movie, MovieRating, UserWatchList, Actor, Director
from django.db import transaction


# Create your views here.

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
            messages.success(request, "Profile created successfully. Login to continue")
            return redirect('/login')
    return render(request, 'account/register.html')


def logout_page(request):
    logout(request)
    return redirect('/login')


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
    user_id = request.user.id
    user_rating = MovieRating.objects.filter(
        user_id=user_id,
        movie_id=movie_id).values('rating')
    print(user_rating)
    if user_rating:
        user_rating = user_rating[0]['rating']
    else:
        user_rating = False
 
    return render(request,
                  template_name='movies/movie_detail.html',
                  context={'movie': movie,
                           'casts': casts,
                           'directors': directors,
                           'user_rating': user_rating,
                           })


def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    movie.delete()
    return redirect('/')


def update_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    casts = movie.actors.values()
    directors = movie.directors.values()

    if request.method == 'POST':
        # Retrieve updated data from the form
        title = request.POST.get('title')
        average_rating = request.POST.get('average_rating')
        release_year = request.POST.get('release_year')
        duration = request.POST.get('duration')
        director_input = request.POST.get('director')
        casts_input = request.POST.get('casts')

        with transaction.atomic():
            movie.title = title
            movie.average_rating = average_rating
            movie.release_year = release_year
            movie.duration = duration

            # Clear existing actors and directors
            movie.actors.clear()
            movie.directors.clear()

            # Process and add actors
            actor_names = casts_input.split(',')
            for actor_name in actor_names:
                actor_name = actor_name.strip()  
                if actor_name != '':
                    actor, created = Actor.objects.get_or_create(
                        name=actor_name)
                    movie.actors.add(actor) 

            # Process and add directors
            director_names = director_input.split(',')
            for director_name in director_names:
                director_name = director_name.strip()
                if director_name != '':
                    director, created = Director.objects.get_or_create(
                        name=director_name)
                    movie.directors.add(director)

            movie.save()
        return redirect('/')

    return render(request, 'movies/update_movie.html', {
        'movie': movie,
        'casts': casts,
        'directors': directors
    })


def add_to_watchlist(request, movie_id):
    print("clicked")
    movie = get_object_or_404(Movie, id=movie_id)
    user = request.user
    if request.method == 'POST':
        curr_user_list = UserWatchList.objects.filter(user=user, movie=movie).first()
        if curr_user_list:
            curr_user_list.watched = not curr_user_list.watched
            curr_user_list.save()
        return redirect(f'/profile/{user.id}')
    if not User.objects.filter(username=user).exists():
        return JsonResponse({
            'status': 'user does not exist',
            'message': 'Create account to add movies to watchlist.'})
    # Check if the movie is already in the user's watchlist
    if UserWatchList.objects.filter(user=user, movie=movie).exists():
        return JsonResponse({
            'status': 'exists',
            'message': 'Movie already in watchlist.'})

    # Add the movie to the user's watchlist
    UserWatchList.objects.create(user=user, movie=movie)
    return JsonResponse({
        'status': 'success',
        'message': 'Movie added to watchlist.'})


def profile_page(request, user_id):
    if not request.user.is_authenticated or user_id == 'None':
        messages.error(request, "Login to view watchlist page.")
        return redirect('/login')
    user_id = int(user_id)
    if request.user.id != user_id:
        messages.error(request,
                       "You don't have permission to view others watchlist.")
        return redirect('/')

    watchlist_info = UserWatchList.objects.select_related('movie').filter(
        user=user_id).values(
        'movie_id',
        'movie__title',
        'id',
        'movie__poster_url',
        'watched'
    )
    rating_info = MovieRating.objects.select_related('movie').filter(
        user=user_id).values('movie__title',
                             'rating',
                             'movie__poster_url',
                             'id')
    print(rating_info)
    return render(request, 'watchlist/watchlist_detail.html',
                  context={'watchlist': watchlist_info,
                           'rating': rating_info})


def search_results(request):

    title_search = request.GET.get('title', None)
    genre_search = request.GET.get('genre', None)
    rating_search = request.GET.get('rating', None)
    director_search = request.GET.get('director', None)
    actor_search = request.GET.get('actor', None)

    filter_movie = Movie.objects.all()

    # Apply filters
    if title_search:
        filter_movie = filter_movie.filter(title__icontains=title_search)

    if genre_search:
        filter_movie = filter_movie.filter(genre__icontains=genre_search)

    if rating_search:
        filter_movie = filter_movie.filter(
            average_rating__gte=float(rating_search))

    if director_search:
        filter_movie = filter_movie.filter(
            directors__name__icontains=director_search)

    if actor_search:
        filter_movie = filter_movie.filter(
            actors__name__icontains=actor_search)

    return render(
        request,
        'search/search_result.html',
        {
            'movies': filter_movie.values(),
        }
        )


@login_required
def rating(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        movie_id = data.get('movie_id')
        user_id = request.user.id
        rating_star = data.get('rating')
        print(user_id, rating_star, movie_id)

        try:
            user = User.objects.get(id=user_id)
            movie = Movie.objects.get(id=movie_id)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User does not exist.'}, status=404)
        except Movie.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Movie does not exist.'}, status=404)

        with transaction.atomic():
            movie_rating, created = MovieRating.objects.update_or_create(
                user=user,
                movie=movie,
                defaults={'rating': rating_star}
            )
            movie_rating.save()
            return JsonResponse({
                'status': 'success', 'message': 'Review added successfully.'})
        return JsonResponse({
            'status': 'error', 'message': 'error while adding to DB.'})
    else:
        # Handle other HTTP methods (GET, etc.) if needed
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method.'}, status=405)


@csrf_exempt
def add_movie_comment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            movie_id = data.get('movie_id')
            user_id = data.get('user_id')
            parent_comment_id = data.get('parent_comment_id')
            content = data.get('content')

            if movie_id is None or user_id is None or content is None:
                raise ValueError("Required fields missing")
            parent_comment = None
            if parent_comment_id:
                parent_comment = MovieComment.objects.get(id=parent_comment_id)

            movie_comment = MovieComment(
                movie_id=movie_id,
                user_id=user_id,
                parent_comment_id=parent_comment,
                content=content,
            )
            movie_comment.save()

            comment_id = movie_comment.id  # Get the comment's ID after saving

            return JsonResponse({'status': 'success',
                                 'message': 'Movie comment added successfully',
                                 'comment_id': comment_id})
        except Exception as e:
            return JsonResponse({'status': 'error', 
                                 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'})


def get_comment_data(request, movie_id):
    # for comments
    comments = MovieComment.objects.filter(
        movie_id=movie_id).select_related(
            'user', 'parent_comment_id').order_by('comment_date')

    comment_data = [
        {
            'userName': comment.user.username,
            'parentCommentId': comment.parent_comment_id.id if comment.parent_comment_id else None,
            'commentId': comment.id,
            'commentContent': comment.content,
            'dateAdded': comment.comment_date
        }
        for comment in comments
    ]
    return JsonResponse(comment_data, safe=False)
