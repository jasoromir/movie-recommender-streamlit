import config as c
import requests
from bs4 import BeautifulSoup
from ast import literal_eval
import numpy as np
import sqlite3
import streamlit as st

def get_poster_path(movie_id):
	r = requests.get(f"{c.MOVIE_DB_URL}movie/{movie_id}")
	soup = BeautifulSoup(r.content, features = 'html.parser')
	for item in soup.findAll('meta'):
		if str(item).split()[1].endswith('.jpg"'):
			return (str(item).split()[1].strip('content=').strip('"'))


def get_director(movie_id, credits):
	crew = credits.loc[credits['id'] == int(movie_id)]['crew']
	crew = literal_eval(crew.values[0])
	for c in crew:
		if c['job'] == 'Director':
			return c['name']
	return "No Name"

def get_main_actors(movie_id, credits):
	cast = credits.loc[credits['id'] == int(movie_id)]['cast']
	cast = literal_eval(cast.values[0])
	actors = [c['name'] for c in cast]
	if len(actors) > 5:
		actors = actors[0:5]
	return actors


def get_genres(movie_id, movies):
	genres = movies.loc[movies['id'] == str(movie_id)]['genres'].values[0]
	genres = literal_eval(genres)
	genre_list = [genre['name'] for genre in genres]
	return genre_list


def weighted_rating(vote_counts, vote_average):
	""" COMPUTE WEIGHTED AVERAGE USING THE FORMULA:
		(v/(v+m) * R) + (m/(v+m) * C)
		v is the number of votes for the movie
		m is the minimum votes required to be listed in the chart
		R is the average rating of the movie
		C is the mean vote across the whole report
	"""
	v = vote_counts
	m = np.min(v)
	R = vote_average
	C = np.mean(R)

	return ((v/(v+10*m) * R)
	     +  (10*m/(v+10*m) * C))

def connect_db():
	# Establish connection with our database
	connection = sqlite3.connect(c.DB_FILE)
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	return cursor

def get_genres():
	cursor = connect_db()

	cursor.execute("""SELECT * FROM genres ORDER BY name""")
	genres = cursor.fetchall()
	genres = [genre['name'] for genre in genres]
	genres.append('ALL')
	return genres

def get_movie_range():
	cursor = connect_db()

	cursor.execute("""SELECT MAX(strftime("%Y", release_date)) as newest,
	MIN(strftime("%Y", release_date)) as oldest
 	FROM movies""")
	dates = cursor.fetchone()
	oldest = dates['oldest']
	newest = dates['newest']
	return oldest, newest

def get_movies(selected_genre, years, images_per_page = 30, offset = 0):

	cursor = connect_db()

	if selected_genre != 'ALL':
		cursor.execute(""" 
			SELECT DISTINCT(movies.id), title, poster_path, scores
			FROM movies 
			JOIN movie_genres 
				ON movies.id = movie_genres.movie_id
			JOIN genres
				ON genres.id = movie_genres.genre_id
			WHERE genres.name = ? 
				AND strftime("%Y", movies.release_date) >= ?
				AND strftime("%Y", movies.release_date) <= ?
			ORDER BY scores DESC, title
			LIMIT ? OFFSET ? """, (selected_genre, str(years[0]), str(years[1]), images_per_page, offset*images_per_page))
	else:
		cursor.execute(""" SELECT DISTINCT(id), title, poster_path, scores
			FROM movies
			WHERE strftime("%Y", release_date) >= ?
				AND strftime("%Y", release_date) <= ?
			ORDER BY scores DESC, title
			LIMIT ? OFFSET ?""", (str(years[0]), str(years[1]), images_per_page, offset*images_per_page))

	return cursor.fetchall()

def display_movies(ids, links, titles, scores):
	components = dict()
	prev_id = 0
	for idx,(m_id, link, title, score) in enumerate(zip(ids, links, titles, scores)):
		components[m_id] = dict()
		components[m_id]["link"] = link
		components[m_id]["title"] = title
		components[m_id]["score"] = score

		row = idx //c.MOVIES_PER_ROW
		col = idx % c.MOVIES_PER_ROW
		
		components[m_id]["row"] = row

		if col == 0:
			components[m_id]["container"] = st.beta_container()
			cols = components[m_id]["container"].beta_columns(5)
		else:
			components[m_id]["container"] = components[prev_id]["container"]

		prev_id = m_id

		components[m_id]["col"] = cols[col]
		components[m_id]["col"].write(f"**{title[0:20] }** \n\n ({score})")
		#components[m_id]["col"].write(f"{components[m_id]["title"]} | {components[m_id]["score"]}")
		components[m_id]["col"].image(components[m_id]["link"], width=180)
		components[m_id]["slider"] = components[m_id]["col"].slider('Like', 0, 5, key = m_id)

def get_recommendation_method():
	rec_method = st.sidebar.selectbox('Recommendation based on:', c.rec_methods, index = 0)
	st.sidebar.write(c.rec_description[rec_method])
	return rec_method