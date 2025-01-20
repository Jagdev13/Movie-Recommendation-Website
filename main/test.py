import pandas as pd
import csv
from django.contrib.auth.models import User
from .models import UserRating, Movie
from django.db import models


df1 = pd.read_csv("C:/Users/amena/Documents/7th sem project/ml-1m/movies.csv", header=0, encoding="Latin1")
links = pd.read_csv("C:/Users/amena/Documents/7th sem project/movie lens dataset/links.csv", header=0)
for row in range(len(df)):
    movies = [Movie(
        movieId = df.iloc[row]['movieId'],
        title = df.iloc[row]['title'],
        genres = df.iloc[row]['genres']
    )]
    Movie.objects.bulk_create(movies)



for row in range(len(df.userId.unique())):
    user = [
        User(
            username = str(row),
            password ='dummy_pw'
    )]
    User.objects.bulk_create(user)


for row in range(len(df)):
    UserRating.objects.create(
        user_id = User.objects.get(username = df.iloc[row]['userId']).id,
        movie_id = Movie.objects.get(movieId = df.iloc[row]['movieId']).movieId,
        rating = df.iloc[row]['rating']
    )

def check_imdbId(imdbId):
    imdbId = str(imdbId)
    x = 7 * str(0)
    new_imdbId = x + imdbId
    new_imdbId = new_imdbId[-7:]
    return "tt" + new_imdbId

for values in range(3953):
    movies = Movie.objects.filter(movieId=values)
    if movies.exists()==True:
        movies = Movie.objects.get(movieId=values)
        movies.imdbId = check_imdbId(int(common.loc[common['movieId'] == values].imdbId.iloc[0]))
        movies.save()
    else:
        pass

