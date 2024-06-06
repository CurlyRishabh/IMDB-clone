from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.db import transaction


# Create your views here.


def movie_list(request):
    movies = ["1", "2"]
    print("in movie_list")
    return render(
        request,
        'movies/movie_list.html',
        {
            'movies': movies,
            'users': User.objects.all().values()
        }
        )


@login_required(login_url='/login')
def movie_detail(request, movie_id):
    movie = movie_id
    return render(request, 'movies/movie_detail.html', {'movie': movie})


def login_page(request):
    print(request)
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
    print('inreq')
    print(request)
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
