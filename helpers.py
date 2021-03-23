import config as c
import requests
from bs4 import BeautifulSoup
from ast import literal_eval
import numpy as np
import sqlite3
import pymysql
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_poster_path(movie_id):
	r = requests.get(f"{c.MOVIE_DB_URL}/movie/{movie_id}")
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


def get_keywords(movie_id, keywords_df):
	keywords = keywords_df.loc[keywords_df['id'] == int(movie_id)]['keywords']
	keywords = literal_eval(keywords.values[0])
	keyword_list = [k['name'] for k in keywords]
	return keyword_list

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
	f = 5 # Punishment for low votes

	return ((v/(v+f*m) * R)
	     +  (f*m/(v+f*m) * C))

def connect_db():
	"""
	Establish connection with our database
	""" 
	# SQLITE3
	# connection = sqlite3.connect(c.DB_FILE)
	# connection.row_factory = sqlite3.Row
	# cursor = connection.cursor()

	# MYSQL
	connection = pymysql.connect(host=c.HOST, user=c.USERNAME, password=c.PASSWORD)
	cursor = connection.cursor(pymysql.cursors.DictCursor)
	#cursor.execute("""USE %s""", (c.DB_NAME,))
	cursor.execute("""USE movies_DB""")
	return cursor

def get_genres_for_display():
	cursor = connect_db()

	cursor.execute("""SELECT * FROM genres ORDER BY name""")
	genres = cursor.fetchall()
	genres = [genre['name'] for genre in genres]
	genres.append('ALL')
	return genres

def get_movie_range():
	cursor = connect_db()

	# SQLITE3
	# cursor.execute("""SELECT MAX(strftime("%Y", release_date)) as newest,
	# MIN(strftime("%Y", release_date)) as oldest
	#FROM movies""")

	# MYSQL
	cursor.execute("""SELECT MAX(YEAR(release_date)) as newest,
		MIN(YEAR(release_date)) as oldest
		FROM movies""")

	dates = cursor.fetchone()
	oldest = dates['oldest']
	newest = dates['newest']
	return oldest, newest

def get_movies(selected_genre, years, images_per_page = 30, offset = 0):
	cursor = connect_db()

	if selected_genre != 'ALL':
		# SQLITE3
		# cursor.execute(""" 
		# 	SELECT DISTINCT(movies.id), title, poster_path, scores
		# 	FROM movies 
		# 	JOIN movie_genres 
		# 		ON movies.id = movie_genres.movie_id
		# 	JOIN genres
		# 		ON genres.id = movie_genres.genre_id
		# 	WHERE genres.name = ? 
		# 		AND strftime("%Y", movies.release_date) >= ?
		# 		AND strftime("%Y", movies.release_date) <= ?
		# 	ORDER BY scores DESC, title
		# 	LIMIT ? OFFSET ? """, (selected_genre, str(years[0]), str(years[1]), images_per_page, offset*images_per_page))

		# MYSQL
		cursor.execute(""" 
			SELECT DISTINCT(movies.id), title, poster_path, scores
			FROM movies 
			JOIN movie_genres 
				ON movies.id = movie_genres.movie_id
			JOIN genres
				ON genres.id = movie_genres.genre_id
			WHERE genres.name = %s 
				AND YEAR(movies.release_date) >= %s
				AND YEAR(movies.release_date) <= %s
			ORDER BY scores DESC, title
			LIMIT %s OFFSET %s """, (selected_genre, str(years[0]), str(years[1]), images_per_page, offset*images_per_page))
	else:
		#SQLITE3
		# cursor.execute(""" SELECT DISTINCT(id), title, poster_path, scores
		# 	FROM movies
		# 	WHERE strftime("%Y", release_date) >= ?
		# 		AND strftime("%Y", release_date) <= ?
		# 	ORDER BY scores DESC, title
		# 	LIMIT ? OFFSET ?""", (str(years[0]), str(years[1]), images_per_page, offset*images_per_page))

		# MYSQL
		cursor.execute(""" SELECT DISTINCT(id), title, poster_path, scores
			FROM movies
			WHERE YEAR(release_date) >= %s
				AND YEAR(release_date) <= %s
			ORDER BY scores DESC, title
			LIMIT %s OFFSET %s""", (str(years[0]), str(years[1]), images_per_page, offset*images_per_page))

	return cursor.fetchall()


def search_movie(name_like):
	cursor = connect_db()
	#SQLITE3
	# cursor.execute(""" SELECT DISTINCT(id), title, poster_path
	# 		FROM movies
	# 		WHERE title LIKE ?
	# 		ORDER BY scores DESC, title
	# 		LIMIT 10 """, (f"%{name_like}%", ))

	#MYSQL
	cursor.execute(""" SELECT DISTINCT(id), title, poster_path
			FROM movies
			WHERE title LIKE %s
			ORDER BY scores DESC, title
			LIMIT 10 """, (f"%{name_like}%", ))
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



def clean_data(data):
	"""
	Function to transform into lowercase and remove spaces between words 
	"""

	# If data is KEYWORDS/GENRES/ACTORS
	if isinstance(data, list):
		return [item.lower().replace(" ", "") for item in data]

	# If data is DIRECTOR
	else:
		return data.lower().replace(" ", "")


def compute_cosine_similarity(features):
	# Count the number of times each "word" appear in the whole corpus
	count = CountVectorizer(stop_words='english')

	# Create the matrix shape -> (movies, corpus)
	count_matrix = count.fit_transform(features)

	# Compute the similarity among all the movies
	cos_sim = cosine_similarity(count_matrix, count_matrix)

	np.save(f"{c.current_dir}/data/cos_sim_matrix_small.npy", cos_sim)

	return cos_sim


def compute_sim_mat():
	cursor = connect_db()

	cursor.execute("""SELECT id, title, director FROM movies """)
	data = cursor.fetchall()

	movie_id = [d['id'] for d in data]
	movie_director= [d['director'] for d in data]
	movie_title = [d['title'] for d in data]

	
	total_movies = len(movie_id)
	count = 0
	computing_bar = st.progress(round(count/total_movies*100))
	# FOR EACH MOVIE BUILD A SET OF FEATURES
	movie_features = []
	for (idx, director) in zip(movie_id, movie_director):
		# Get ACTORS
		# cursor.execute("""SELECT name 
		# 	FROM actors 
		# 	JOIN movie_actors ON movie_actors.actor_id = actors.id
		# 	WHERE movie_actors.movie_id = ? """, (idx,))
		cursor.execute("""SELECT name 
			FROM actors 
			JOIN movie_actors ON movie_actors.actor_id = actors.id
			WHERE movie_actors.movie_id = %s """, (idx,))
		data = cursor.fetchall()
		actors = [d['name'] for d in data]

		# Get GENRES
		# cursor.execute("""SELECT name 
		# 	FROM genres 
		# 	JOIN movie_genres ON movie_genres.genre_id = genres.id
		# 	WHERE movie_genres.movie_id = ? """, (idx,))
		cursor.execute("""SELECT name 
			FROM genres 
			JOIN movie_genres ON movie_genres.genre_id = genres.id
			WHERE movie_genres.movie_id = %s """, (idx,))
		data = cursor.fetchall()
		genres = [d['name'] for d in data]

		# GET KEYOWRDS
		# cursor.execute("""SELECT name 
		# 	FROM keywords 
		# 	JOIN movie_keywords ON movie_keywords.keyword_id = keywords.id
		# 	WHERE movie_keywords.movie_id = ? 
		# 	LIMIT 5 """, (idx,))
		cursor.execute("""SELECT name 
			FROM keywords 
			JOIN movie_keywords ON movie_keywords.keyword_id = keywords.id
			WHERE movie_keywords.movie_id = %s 
			LIMIT 5 """, (idx,))
		data = cursor.fetchall()
		keywords = [d['name'] for d in data]


		# PARSE FEATURES: We need to remove spaces, so words like: Traffic Jam are not close to Bread Jam in the feature space
		director = clean_data(director)
		actors   = clean_data(actors)
		genres   = clean_data(genres)
		keywords = clean_data(keywords)

		# COMBINE ALL FEATURES IN A SINGLE VECTOR
		features = f'{director} {" ".join(actors)} {" ".join(genres)} {" ".join(keywords)}' 
		movie_features.append(features)

		count += 1
		computing_bar.progress(round(count/total_movies*100))
	return compute_cosine_similarity(movie_features)


def get_movies_content_based(sorted_scores, years, images_per_page, offset):

	movie_indexes = [score[0]+1 for score in sorted_scores][1:]

	cursor = connect_db()
	# SQLITE3
	# cursor.execute(""" SELECT DISTINCT(id), title, poster_path, scores 
	# 		FROM movies
	# 		WHERE strftime("%Y", release_date) >= ?
	# 			AND strftime("%Y", release_date) <= ?
	# 		ORDER BY id
	# 		""", (str(years[0]), str(years[1])))

	#MYSQL
	cursor.execute(""" SELECT DISTINCT(id), title, poster_path, scores 
			FROM movies
			WHERE YEAR(release_date) >= %s
				AND YEAR(release_date) <= %s
			ORDER BY id
			""", (str(years[0]), str(years[1])))

	movies = cursor.fetchall()

	# Eliminate from movie_indexes, the movies that do not fall in the time range
	ids = [movie['id']-1 for movie in movies]
	movie_indexes = [ids.index(idx) for idx in movie_indexes if idx in ids]


	# COMPONENTS
	scores, titles, ids, links = [], [], [], []
	for idx in range(images_per_page*offset,images_per_page*(offset+1)):

		try:
			movie_idx = movie_indexes[idx]-1
			scores.append(f"Score: {movies[movie_idx]['scores']}")
			titles.append(movies[movie_idx]['title']) 
			ids.append(movie_idx)
			if  movies[movie_idx]['poster_path'] is not None:
				links.append(f"{c.MOVIE_DB_URL}{movies[movie_idx]['poster_path']}")
			else:
				links.append(c.NO_IMAGE)
		except:
			pass




	return (ids, links, titles, scores) 



