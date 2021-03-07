import streamlit as st
import pandas as pd 
import numpy as np 
import config as c
import helpers as h
from ast import literal_eval
import sqlite3


st.set_page_config(page_title="Movie Recommender", layout='wide')
st.title('Movies Recomender with Streamlit')


# GENRE SELECT
genres = h.get_genres()
selected_genre = st.sidebar.selectbox('Select Genre', sorted(genres), index = 0)


# YEAR SLIDER
oldest, newest = h.get_movie_range()
years = st.sidebar.slider('Movies between:', int(oldest), int(newest), (int(oldest), int(newest)))


# GET MOVIES
images_per_page = st.sidebar.slider('Images per page', 5, 60, value = 30, step = 5)
offset = st.sidebar.slider(f"<- Navigate through pages ->", 0, 10, value = 0, step = 1)
movies_db = h.get_movies(selected_genre, years, images_per_page, offset)


# RECOMMENDATION METHOD
rec_method = h.get_recommendation_method()


# DISPLAY SELECTION
if selected_genre != 'ALL':
	st.markdown(f"## **List of Best {selected_genre} Movies between {years[0]} - {years[1]}**")
else:
	st.markdown(f"## **List of Best Movies between {years[0]} - {years[1]}**")


# COMPONENTS
scores = [f"Score: {movie['scores']}" for movie in movies_db]
titles = [movie['title'] for movie in movies_db]
ids = [movie['id'] for movie in movies_db]
links = [f"{c.MOVIE_DB_URL}{movie['poster_path']}" if movie['poster_path'] is not None else c.NO_IMAGE for movie in movies_db ]


# DISPLAY MOVIES
components = h.display_movies(ids, links, titles, scores)




