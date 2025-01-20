
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from .forms import RegisterUser, EditProfile
from .models import Movie, UserRating
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from .recommendation import recommend  
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


import requests
import pandas as pd




def get_movie_details(imdbId):
    url = "http://www.omdbapi.com/?apikey=a23d4f9a&i=" + str(imdbId)
    response = requests.get(url)
    movie_data = response.json()
    return movie_data




def homepage(request):
    
    if request.method == "POST":
        form = RegisterUser(request.POST)
        if form.is_valid():
            # Save user with a hashed password
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()

            # Automatically log in the user after registration
            login(request, user)
            messages.success(request, f'Account created for {form.cleaned_data["username"]}!')
            return redirect("homepage")  # Redirect to homepage after registration
        else:
            # Display the form with errors
            return render(request, "main/register.html", {"form": form})

    # Handle GET requests - display homepage content
    form = RegisterUser()  # Empty form for new registrations
    slider_images = ["static/images/Slider1.jpg", "static/images/Slider2.jpg", "static/images/Slider3.jpg"]

    # Get all movies or filter by search query
    query = request.GET.get('q')
    movies = Movie.objects.filter(title__icontains=query).distinct()[:8] if query else Movie.objects.all()[:8]

    # Movie posters for search results
    movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/default_poster.jpg'))
        for movie in movies
    ]

    # Fetch comedy and drama movies
    comedy_movies = Movie.objects.filter(genres__icontains="Comedy").order_by('title')[:8]
    drama_movies = Movie.objects.filter(genres__icontains="Drama").order_by('title')[:8]

    # Posters for comedy and drama movies
    comedy_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/default_poster.jpg'))
        for movie in comedy_movies
    ]
    drama_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/default_poster.jpg'))
        for movie in drama_movies
    ]

    # Recommended movies logic
    user_id = request.user.id if request.user.is_authenticated else None
    if user_id:
        rated_movies = UserRating.objects.filter(user_id=user_id).values_list('movie_id', flat=True)
        recommended_movies = Movie.objects.filter(movieId__in=rated_movies).order_by('title')[:10]
    else:
        recommended_movies = Movie.objects.order_by('title')[:10]  # Popular movies as fallback

    recommended_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/Slider1.jpg'))
        for movie in recommended_movies
    ]

    # Pass context data to template
    context = {
        'form': form,
        'movies_and_posters': movies_and_posters,
        'comedy_movies_and_posters': comedy_movies_and_posters,
        'drama_movies_and_posters': drama_movies_and_posters,
        'recommended_movies_and_posters': recommended_movies_and_posters,
        'slider_images': slider_images,
        'recommended_movies_tag': "Your Recommended Movies"
    }

    return render(request, 'main/index.html', context)







def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register')

@login_required(login_url='log_in')
def user_profile(request):
    if request.method == "POST":
        form = EditProfile(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('homepage')
        else:
            return render(request, "main/profile.html", {"form": form})
    form = EditProfile(auto_id=True, instance=request.user)
    return render(request, "main/profile.html", {"form": form})


def log_in(request): 
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Check if the request is an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'username': username})
            else:
                messages.info(request, f"Logged in as {username}.")
                return redirect("homepage")
        else:
            # Return error message for AJAX and non-AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'error_message': 'Invalid credentials'})
            else:
                return render(request, 'main/index.html', {'error_message': 'Invalid Credentials.'})
    
    return render(request, "main/index.html")
def log_out(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("homepage")



def movie_list(request):
    # Retrieve the selected genre from the request
    selected_genre = request.GET.get('genre', None)

    # Retrieve distinct genres for the filter dropdown
    genres = Movie.objects.values_list('genres', flat=True).distinct()

    # Filter movies by the selected genre (if provided)
    if selected_genre:
        movies = Movie.objects.filter(genres=selected_genre).order_by('title')
    else:
        # If no genre is selected, show all movies
        movies = Movie.objects.all().order_by('title')

    # Set up pagination
    paginator = Paginator(movies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch posters for movies in the page
    poster_path = []
    for movie in page_obj.object_list:
        try:
            movie_details = get_movie_details(movie.imdbId)
            poster_link = movie_details.get('Poster', '/static/images/default-poster.jpg')
            poster_path.append(poster_link)
        except KeyError:
            poster_path.append('/static/images/default-poster.jpg')

    # Combine the movies with their posters
    movies_and_posters = zip(page_obj.object_list, poster_path)

    # Render the template with the necessary context
    return render(
        request,
        "main/list.html",
        {
            "movies_and_posters": movies_and_posters, 
            "page_obj": page_obj,
            "genres": genres,  # Pass the genres for the filter
            "selected_genre": selected_genre  # Pass the selected genre to keep the filter in place
        }
    )



def comedy(request):
    # Get Comedy and Drama movies separately, limited to a fixed number for display
    comedy_movies = Movie.objects.filter(genres="Comedy").order_by('title')[:30]  # Showing 10 movies
    drama_movies = Movie.objects.filter(genres="Drama").order_by('title')[:30]    # Showing 10 movies

    # Fetch posters for each movie with error handling for missing 'Poster' key
    comedy_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/default_poster.png'))
        for movie in comedy_movies
    ]
    drama_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/default_poster.png'))
        for movie in drama_movies
    ]

    # Recommended movies based on user ratings
    user_id = request.user.id
    rated_movies = UserRating.objects.filter(user_id=user_id).values_list('movie_id', flat=True)

    if rated_movies:
        # Get genres of movies the user has rated
        rated_genres = Movie.objects.filter(movieId__in=rated_movies).values_list('genres', flat=True).distinct()
        
        # Recommend movies from the same genres that the user has rated
        recommended_movies = Movie.objects.filter(movieId__in=rated_movies).order_by('title')[:10]  # Only movies the user has rated
    else:
        # If the user has no ratings, recommend popular movies (for example)
        recommended_movies = Movie.objects.filter(genres="Comedy")[:10]  # Adjust this as needed

    # Fetch posters for recommended movies with error handling
    recommended_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/Slider1.jpeg'))
        for movie in recommended_movies
    ]

    return render(request, "main/comedy.html", {
        "comedy_movies_and_posters": comedy_movies_and_posters,
        "drama_movies_and_posters": drama_movies_and_posters,
        "recommended_movies_and_posters": recommended_movies_and_posters,
        "recommended_movies_tag": "Your Recommended Movies"  # Add this to indicate the movies are rated by the user
    })
def index(request):
    # Get Comedy and Drama movies separately, limited to a fixed number for display
    comedy_movies = Movie.objects.filter(genres="Comedy").order_by('title')[:30]
    drama_movies = Movie.objects.filter(genres="Drama").order_by('title')[:30]

    # Fetch posters for each movie with error handling for missing 'Poster' key
    comedy_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/default_poster.png'))
        for movie in comedy_movies
    ]
    drama_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/default_poster.png'))
        for movie in drama_movies
    ]

    # Recommended movies based on user ratings
    user_id = request.user.id
    rated_movies = UserRating.objects.filter(user_id=user_id).values_list('movie_id', flat=True)

    if rated_movies:
        rated_genres = Movie.objects.filter(movieId__in=rated_movies).values_list('genres', flat=True).distinct()
        recommended_movies = Movie.objects.filter(movieId__in=rated_movies).order_by('title')[:10]
    else:
        recommended_movies = Movie.objects.filter(genres="Comedy")[:10]

    # Fetch posters for recommended movies with error handling
    recommended_movies_and_posters = [
        (movie, get_movie_details(movie.imdbId).get('Poster', '/static/images/Slider1.jpeg'))
        for movie in recommended_movies
    ]

    return render(request, "index.html", {
        "comedy_movies_and_posters": comedy_movies_and_posters,
        "drama_movies_and_posters": drama_movies_and_posters,
        "recommended_movies_and_posters": recommended_movies_and_posters,
        "recommended_movies_tag": "Your Recommended Movies"
    })

from django.http import Http404

def movies_rated_by_user(request):
    user = request.user.id
    movies_rated = UserRating.objects.filter(user_id=user)
    id_of_movies_rated = [movie['movie_id'] for movie in movies_rated.values('movie_id')]

    poster_path = []
    movies = []

    for movie_id in id_of_movies_rated:
        try:
            # Fetch the movie, handling potential DoesNotExist error
            movie = Movie.objects.get(movieId=movie_id)
            movies.append(movie)

            # Fetch the poster, handling missing Poster data
            movie_details = get_movie_details(movie.imdbId)
            poster_link = movie_details.get('Poster', '/static/images/default-poster.jpg')
            poster_path.append(poster_link)
        except Movie.DoesNotExist:
            # Log error or skip movie if it doesn't exist
            continue
        except KeyError:
            # Fallback in case 'Poster' key is missing in get_movie_details
            poster_path.append('/static/images/default-poster.jpg')

    paginator = Paginator(movies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    movie_page = page_obj.object_list

    paginator_poster = Paginator(poster_path, 12)
    page_obj_poster = paginator_poster.get_page(page_number)
    poster_page = page_obj_poster.object_list

    movies_and_posters = zip(movie_page, poster_page)

    return render(
        request,
        template_name='main/watched_list.html',
        context={"movies_and_posters": movies_and_posters, "page_obj": page_obj}
    )





def movies_rated_by_user1(request):
    user = request.user.id
    movies_rated = UserRating.objects.filter(user_id=user)
    id_of_movies_rated = [movie['movie_id'] for movie in movies_rated.values('movie_id')]
    movies = [Movie.objects.get(movieId=movie_id) for movie_id in id_of_movies_rated]
    poster_path = [get_movie_details(movie.imdbId)['Poster'] for movie in movies]
    paginator = Paginator(movies, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    movies_and_posters = zip(page_obj.object_list, poster_path)

    print(movies_and_posters)
    return render(request, 'main/contact_us.html', {"movies_and_posters": movies_and_posters, "page_obj": page_obj})









@login_required(login_url='log_in')
def details(request, pk):
    movie = Movie.objects.get(movieId=pk)
    movie_details = get_movie_details(movie.imdbId)
    old_rating = UserRating.objects.filter(user_id=request.user.id, movie_id=pk).first()
    if request.method == "POST":
        rating = request.POST['rating']
        UserRating.objects.update_or_create(user_id=request.user.id, movie_id=pk, defaults={'rating': rating})
        messages.success(request, "Your rating has been submitted.")
        old_rating = rating
    return render(request, 'main/details.html', {"movies": movie, "movie_details": movie_details, "old_rating": old_rating})



@login_required(login_url='log_in') 
@cache_page(60 * 3)
@vary_on_cookie
def recommend_movies(request):
    user = request.user.id

    # Check if user has rated enough movies
    user_ratings_count = UserRating.objects.filter(user_id=user).count()
    if user_ratings_count < 12:
        messages.info(request, f"Please rate at least 12 movies to get recommendations. You have rated {user_ratings_count} movies.")
        return redirect('movie_list')

    try:
        # Fetch recommendations
        recommendations = recommend(user)
        if not recommendations:
            messages.error(request, "Unable to generate recommendations. Please try rating more diverse movies.")
            return redirect('movie_list')

        # Fetch all movies for recommendations
        movies = Movie.objects.filter(movieId__in=recommendations)

        # Handle genre filtering
        selected_genre = request.GET.get('genre', '')
        if selected_genre:
            movies = movies.filter(genres__icontains=selected_genre)

        # Fetch posters for the filtered movies
        movies_and_posters = []
        for movie in movies:
            try:
                movie_details = get_movie_details(movie.imdbId)
                poster = movie_details.get('Poster', '/static/images/default-poster.jpg')
                movies_and_posters.append((movie, poster))
            except Exception as e:
                print(f"Error fetching movie {movie.movieId}: {str(e)}")
                continue

        # Get all unique genres for the dropdown
        all_genres = set()
        for movie in Movie.objects.all():
            all_genres.update(genre.strip() for genre in movie.genres.split(','))

        # Sort genres alphabetically
        sorted_genres = sorted(all_genres)

        return render(request, 'main/recommendation.html', {
            "movies_and_posters": movies_and_posters,
            "recommendation_count": len(movies),
            "genres": sorted_genres,
            "selected_genre": selected_genre,  # Pass the selected genre to the template
        })

    except Exception as e:
        messages.error(request, f"An error occurred while generating recommendations: {str(e)}")
        return redirect('movie_list')


@login_required(login_url='log_in')
def delete_rating(request, pk):
    UserRating.objects.filter(user_id=request.user.id, movie_id=pk).delete()
    messages.success(request, "Rating successfully deleted.")
    return redirect("details", pk=pk)

def about_us(request):
    return render(request, 'main/about_us.html')

def contact_us(request):
    return render(request, 'main/contact_us.html')
