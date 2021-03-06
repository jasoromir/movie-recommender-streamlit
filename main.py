import streamlit as st
import pandas as pd 
import numpy as np 
import config as c
import helpers as h
from ast import literal_eval
import sqlite3


st.title('Streamlit for Movies Recomender')

movies = pd.read_csv(c.DATA_PATH + 'movies_metadata.csv', low_memory = False)
genre_list = set()
for movie_gen in movies.genres:
  list_gen = literal_eval(movie_gen)
  for genre in list_gen:
    genre_list.add(genre['name'])

selected_genre = st.sidebar.selectbox('Select Genre', sorted(list(genre_list)))


# Get images
# Establish connection with our database
connection = sqlite3.connect(c.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("""
	SELECT title, poster_path
	FROM movies
	ORDER BY title
	""")

movies_db = cursor.fetchall()
st.text(movies_db[0])

titles = [title['title'] for title in movies_db]
links = [f"https://www.themoviedb.org/{link['poster_path']}" for link in movies_db]


st.image(links ,width=100 , caption = titles)
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
