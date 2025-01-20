"""RecommendationWebApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
'''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('register/', views.register, name="register"),
    path('log_in/', views.log_in , name="log_in"),
    path('log_out/', views.log_out , name="log_out"),
    path('movie/<int:pk>/', views.details, name="details"),
    path('recommendations/', views.recommend_movies, name='recommend'),
    path('list/', views.movie_list, name='movie_list'),
    path('watch_list/', views.movies_rated_by_user, name='watch_list'),
    path('profile/', views.user_profile, name='profile'),
    path('delete_rating/<int:pk>', views.delete_rating, name ="delete_rating")
]'''

from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    
    
    path('log_in/', views.log_in, name="log_in"),
    path('log_out/', views.log_out, name="log_out"),
    path('movie/<int:pk>/', views.details, name="details"),
    path('recommendations/', views.recommend_movies, name='recommend'),
    path('list/', views.movie_list, name='movie_list'),
    
    path('watch_list/', views.movies_rated_by_user, name='watch_list'),
    
    path('profile/', views.user_profile, name='profile'),
    path('delete_rating/<int:pk>', views.delete_rating, name="delete_rating"),
    path('about_us/', views.about_us, name="about_us"),  # New About Us page
    path('contact_us/', views.contact_us, name="contact_us"),  # New Contact Us page
    
    path('contact_us/', views.movies_rated_by_user1, name='watch_list1'),
    path('comedy/', views.comedy, name='comedy'),
    

]




