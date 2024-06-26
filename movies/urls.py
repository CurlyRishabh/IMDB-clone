from django.urls import path
from . import views as movie_view

urlpatterns = [
    path('', movie_view.movie_list, name='movie_list'),
    path('movies/<int:movie_id>/',
         movie_view.movie_detail,
         name='movie_detail'),
    path('add_to_watchlist/<int:movie_id>/', movie_view.add_to_watchlist, name='movie_list'),
    path('profile/<str:user_id>/', movie_view.profile_page, name='profile_page'),
    path('login/', movie_view.login_page, name='login_page'),
    path('register/', movie_view.register_page, name='register_page'),
    path('logout/', movie_view.logout_page, name='logout_page'),

    path('search/', movie_view.search_results, name='search_page'),
    path('rating/', movie_view.rating, name='rating_handler'),
    path('add_movie_comment/', movie_view.add_movie_comment,
         name="comment_handler"),

    path('get_movie_comments/<int:movie_id>', movie_view.get_comment_data,
         name='get_comment_data'),

    path('deletemovie/<int:movie_id>/', movie_view.delete_movie,
         name='delete_movie'),

    path('updatemovie/<int:movie_id>/', movie_view.update_movie,
         name='update_movie'),

]
