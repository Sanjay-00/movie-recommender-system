import streamlit as st
import pickle
import pandas as pd
import requests
import os
import numpy as np  # Import numpy

# Load the movie list as before
movies_list = pickle.load(open('movies.pkl', 'rb'))
movies_df = pd.DataFrame(movies_list)

# Function to load similarity chunks and concatenate them
def load_similarity_chunks():
    similarity_chunks = []
    for filename in sorted(os.listdir('similarity_chunks')):
        with open(os.path.join('similarity_chunks', filename), 'rb') as f:
            similarity_chunks.append(pickle.load(f))
    
    # Use numpy to concatenate the chunks along axis 0 (rows)
    return np.vstack(similarity_chunks)

# Load the split similarity matrix
similarity = load_similarity_chunks()

# Function to fetch movie poster using The Movie Database API
def fetch_poster(movie_id):
    api_key = "8265bd1679663a7ea12ac168da84d2e8"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    full_poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_poster_url

# Function to recommend movies based on similarity
def recommend_movie(movie_title):
    # Get the index of the selected movie
    movie_index = movies_df[movies_df['title'] == movie_title].index[0]
    
    # Get similarity scores for that movie
    distances = similarity[movie_index]
    
    # Sort movies based on similarity, exclude the first result (the same movie)
    sorted_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    # Prepare list of recommended movies and their posters
    recommended_movies = []
    recommended_posters = []
    
    for i in sorted_movies:
        movie_id = movies_df.iloc[i[0]].id
        recommended_movies.append(movies_df.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_posters

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #1c1c1c;
    }
    .title {
        font-size: 45px;
        font-weight: bold;
        color: white;
        text-align: center;
        margin-top: -30px;
        margin-bottom: 20px;
    }
    .recommendation-title {
        font-size: 25px;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
    }
    .movie-title {
        font-size: 18px;
        font-weight: bold;
        color: white;
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# App Title
st.markdown('<p class="title">🎬 Movie Recommender System</p>', unsafe_allow_html=True)

# Dropdown menu to select a movie
selected_movie_name = st.selectbox(
    "Select a Movie to get similar recommendation",
    movies_df['title'].values,
    help="Choose a movie from the dropdown to get similar recommendations"
)

# Show movie recommendations when the button is clicked
if st.button('Show Recommendations'):
    recommended_movies, recommended_posters = recommend_movie(selected_movie_name)
    
    # Display recommended movies and posters
    st.markdown('<p class="recommendation-title">Recommended Movies:</p>', unsafe_allow_html=True)
    
    # Create 5 columns for displaying movie posters and titles
    columns = st.columns(5)
    
    for i, col in enumerate(columns):
        with col:
            st.image(recommended_posters[i])
            st.markdown(f'<p class="movie-title">{recommended_movies[i]}</p>', unsafe_allow_html=True)
