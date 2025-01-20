import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from main.models import Movie, UserRating

def recommend(user):
    # Fetch data from the database
    rating = pd.DataFrame(UserRating.objects.all().values())
    movies = pd.DataFrame(Movie.objects.all().values())
    
    # Early exit if data is insufficient
    if rating.empty or movies.empty:
        print("No data found in ratings or movies.")
        return []
        
    if len(rating[rating['user_id'] == user]) < 1:
        print("No ratings found for this user.")
        return []

    # Calculate mean ratings per user
    mean_ratings = rating.groupby(by='user_id', as_index=False)['rating'].mean()
    
    # Merge and adjust ratings
    avg_rating = pd.merge(rating, mean_ratings, on='user_id', suffixes=('_x', '_y'))
    avg_rating['adj_movie_rating'] = avg_rating['rating_x'] - avg_rating['rating_y']
    
    # Create pivot table for user-movie interactions
    user_movie_table = pd.pivot_table(avg_rating, values='adj_movie_rating', index='user_id', columns='movie_id', fill_value=0)
    
    # Handle missing user in the table
    if user not in user_movie_table.index:
        print(f"User {user} not found in the ratings table.")
        return []
    
    # Compute similarity matrix using cosine similarity
    cosine_sim = cosine_similarity(user_movie_table)
    np.fill_diagonal(cosine_sim, 0)
    similar_users_df = pd.DataFrame(cosine_sim, index=user_movie_table.index, columns=user_movie_table.index)
    
    # Select top similar users
    n_neighbours = min(25, len(similar_users_df) - 1)  # Limit to a maximum of 25 users
    user_similarities = similar_users_df.loc[user].sort_values(ascending=False).iloc[:n_neighbours]
    
    # Gather movies rated by similar users
    similar_users_movies = rating[rating['user_id'].isin(user_similarities.index)]
    
    # Calculate movie scores based on ratings from similar users
    movie_scores = similar_users_movies.groupby('movie_id')['rating'].agg(['mean', 'count'])
    movie_scores = movie_scores[movie_scores['count'] > 2]  # Retain movies with more than 2 ratings
    
    # Exclude movies already rated by the current user
    user_rated_movies = rating[rating['user_id'] == user]['movie_id'].tolist()
    recommended_movies = movie_scores.index.difference(user_rated_movies)
    
    # Sort recommendations by the average rating
    sorted_recommendations = movie_scores.loc[recommended_movies].sort_values('mean', ascending=False)
    
    # Return top 20 movie recommendations
    return sorted_recommendations.index[:50].tolist()