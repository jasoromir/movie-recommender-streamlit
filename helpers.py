import config as c
import requests
from bs4 import BeautifulSoup
from ast import literal_eval
import numpy as np

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