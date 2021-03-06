import streamlit as st
import pandas as pd 
import numpy as np 
import config as c
import helpers as h
from ast import literal_eval
import sqlite3

st.set_page_config(page_title="Movie Recommender", layout='wide')

st.title('Movies Recomender with Streamlit')


# Establish connection with our database
connection = sqlite3.connect(c.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# GENRE SELECT
cursor.execute("""SELECT * FROM genres ORDER BY name""")
genres = cursor.fetchall()
genres = [genre['name'] for genre in genres]
genres.append('ALL')
selected_genre = st.sidebar.selectbox('Select Genre', sorted(genres), index = 0)

# YEAR SLIDER
cursor.execute("""SELECT MAX(strftime("%Y", release_date)) as newest,
	MIN(strftime("%Y", release_date)) as oldest
 	FROM movies""")
dates = cursor.fetchone()
oldest = dates['oldest']
newest = dates['newest']

years = st.sidebar.slider('Movies between:', int(oldest), int(newest), (int(oldest), int(newest)))



# Get images
if selected_genre != 'ALL':
	st.markdown(f"## **List of Best {selected_genre} Movies between {years[0]} - {years[1]}**")
	cursor.execute(""" 
		SELECT title, poster_path, scores
		FROM movies 
		JOIN movie_genres 
			ON movies.id = movie_genres.movie_id
		JOIN genres
			ON genres.id = movie_genres.genre_id
		WHERE genres.name = ? 
			AND strftime("%Y", movies.release_date) >= ?
			AND strftime("%Y", movies.release_date) <= ?
		ORDER BY scores DESC, title
		LIMIT 30 """, (selected_genre,str(years[0]), str(years[1])))
else:
	st.markdown(f"## **List of Best Movies between {years[0]} - {years[1]}**")
	cursor.execute(""" SELECT title, poster_path, scores
		FROM movies
		WHERE strftime("%Y", release_date) >= ?
			AND strftime("%Y", release_date) <= ?
		ORDER BY scores DESC, title
		LIMIT 30""", (str(years[0]), str(years[1])))

movies_db = cursor.fetchall()


scores = [f"Score: {movie['scores']}" for movie in movies_db]
titles = [title['title'] for title in movies_db]
captions = [caption for caption in zip(titles, scores)]
default_link = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Image-missing.svg/480px-Image-missing.svg.png"
links = [f"https://www.themoviedb.org/{link['poster_path']}" if link['poster_path'] is not None else default_link for link in movies_db ]


st.image(links ,width=180 , caption =captions)
# # 10% most voted movies
# C = metadata['vote_average'].mean()
# m = metadata['vote_count'].quantile(0.9)
# most_voted_movies = metadata.loc[metadata['vote_count'] >= m]

# def weighted_rating(df, m = m, C = C):
# 	""" COMPUTE WEIGHTED AVERAGE USING THE FORMULA:
# 		(v/(v+m) * R) + (m/(v+m) * C)
# 		v is the number of votes for the movie
# 		m is the minimum votes required to be listed in the chart
# 		R is the average rating of the movie
# 		C is the mean vote across the whole report
# 	"""

# 	vote = df['vote_count']
# 	vote_average = df['vote_average']

# 	return ((vote/(vote+m) * vote_average)
# 	    +  (m/(vote + m) * C))


# most_voted_movies['score'] = most_voted_movies.apply(weighted_rating, axis = 1)

# most_voted_movies = most_voted_movies.sort_values('score', ascending=False)

# print(most_voted_movies[['title', 'genres', 'vote_count', 'vote_average', 'score']].head(20))
# print(most_voted_movies.genres[0].name.head(20))
