from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


# Create your models here.
class Movie(models.Model):
    movieId = models.IntegerField(primary_key=True, unique=True)
    title = models.CharField(max_length=100)
    genres = models.CharField(max_length=100)
    imdbId = models.CharField(default=None, max_length=9)

    def __str__(self):
        return self.title

class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(5)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='user_rating')
        ]