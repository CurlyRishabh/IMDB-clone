from django.urls import path
from . import views as movie_view

urlpatterns = [
    path('', movie_view.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/',
         movie_view.movie_detail,
         name='movie_detail'),

    path('login/', movie_view.login_page, name='login_page'),
    path('register/', movie_view.register_page, name='register_page'),
]
