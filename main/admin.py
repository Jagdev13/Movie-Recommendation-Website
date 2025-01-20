from django.contrib import admin
from .models import Movie, UserRating

# Register your models here.\

admin.site.register(UserRating)
admin.site.register(Movie)

