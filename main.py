import streamlit as st
import pandas as pd 
import numpy as np 
import config as c
import helpers as h
from ast import literal_eval
import sqlite3
import content_based_rec


st.set_page_config(page_title="Movie Recommender", layout='wide')
st.title('Movies Recomender with Streamlit')


# GENRE SELECT
genres = h.get_genres()
selected_genre = st.sidebar.selectbox('Select Genre', sorted(genres), index = 0)


# YEAR SLIDER
oldest, newest = h.get_movie_range()
years = st.sidebar.slider('Movies between:', int(oldest), int(newest), (int(oldest), int(newest)))


# GADGETS TO DISPLAY MOVIES
images_per_page = st.sidebar.slider('Images per page', 5, 60, value = 30, step = 5)
offset = st.sidebar.slider(f"<- Navigate through pages ->", 0, 10, value = 0, step = 1)


# RECOMMENDATION METHOD
rec_method = h.get_recommendation_method()
if rec_method == 'Generalized recommendations':

	# DISPLAY SELECTION
	if selected_genre != 'ALL':
		st.markdown(f"## **List of Best {selected_genre} Movies between {years[0]} - {years[1]}**")
	else:
		st.markdown(f"## **List of Best Movies between {years[0]} - {years[1]}**")

	# GET MOVIES TO RECOMMEND
	movies_db = h.get_movies(selected_genre, years, images_per_page, offset)

	# COMPONENTS
	scores = [f"Score: {movie['scores']}" for movie in movies_db]
	titles = [movie['title'] for movie in movies_db]
	ids = [movie['id'] for movie in movies_db]
	links = [f"{c.MOVIE_DB_URL}{movie['poster_path']}" if movie['poster_path'] is not None else c.NO_IMAGE for movie in movies_db ]


	# DISPLAY MOVIES
	components = h.display_movies(ids, links, titles, scores)


elif rec_method == 'Content-based recommendations':
	name_like = st.sidebar.text_input("Recommend movies like:", 'Title starts like...')
	searched = h.search_movie(name_like)

	movies_titles = [search['title'] for search in searched]
	movies_idx = [search['id'] for search in searched]
	movie_links = [search['poster_path'] for search in searched]

	movie_name = st.sidebar.selectbox('', movies_titles)
	try:
		movie_id = movies_idx[movies_titles.index(movie_name)]
		st.sidebar.image(f"{c.MOVIE_DB_URL}{movie_links[movies_titles.index(movie_name)]}")
		st.markdown(f"## **List of Movies similar to {movie_name} between {years[0]} - {years[1]}**")

		content_based_rec.get_recommendations(movie_id, years, images_per_page, offset)
	except Exception as e:
		st.markdown(f"## **Search for a movie in the Sidebar**")
		st.write(e)









