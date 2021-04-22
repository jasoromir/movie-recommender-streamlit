from utils  import function_cm as cm
from config import config as c

import streamlit as st
import numpy as np
import pymysql
import requests
import time
import pickle
from bs4 import BeautifulSoup
from ast import literal_eval
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

@st.cache
def get_genres_for_display():
	cursor = connect_db()

	cursor.execute("""SELECT * FROM genres ORDER BY name""")
	genres = cursor.fetchall()
	genres = [genre['name'] for genre in genres]
	genres.append('ALL')
	return genres

@st.cache
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

@st.cache
def get_movies(selected_genre, years, images_per_page = 30, offset = 0, *user_id):
	cursor = connect_db()
	if user_id:
		if selected_genre != 'ALL':
			cursor.execute(""" 
				SELECT DISTINCT(movies.id), title, poster_path, scores, rating
				FROM movies 
				JOIN movie_genres 
					ON movies.id = movie_genres.movie_id
				JOIN genres
					ON genres.id = movie_genres.genre_id
				JOIN user_ratings
					ON user_ratings.movie_id = movies.id
				WHERE genres.name = %s 
					AND YEAR(movies.release_date) >= %s
					AND YEAR(movies.release_date) <= %s
					AND user_ratings.user_id = %s
				ORDER BY rating DESC, scores DESC, title
				LIMIT %s OFFSET %s """, (selected_genre, str(years[0]), str(years[1]), user_id, images_per_page, offset*images_per_page))
		else:
			cursor.execute(""" SELECT DISTINCT(movies.id), title, poster_path, scores, rating
				FROM movies
				JOIN user_ratings
					ON user_ratings.movie_id = movies.id
				WHERE YEAR(release_date) >= %s
					AND YEAR(release_date) <= %s
					AND user_ratings.user_id = %s
				ORDER BY rating DESC, scores DESC, title
				LIMIT %s OFFSET %s""", (str(years[0]), str(years[1]), user_id, images_per_page, offset*images_per_page))
	else:
		if selected_genre != 'ALL':
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
			cursor.execute(""" SELECT DISTINCT(id), title, poster_path, scores
				FROM movies
				WHERE YEAR(release_date) >= %s
					AND YEAR(release_date) <= %s
				ORDER BY scores DESC, title
				LIMIT %s OFFSET %s""", (str(years[0]), str(years[1]), images_per_page, offset*images_per_page))

	return cursor.fetchall()

@st.cache
def get_usernames():
	cursor = connect_db()
	cursor.execute(""" 
			SELECT username, id
			FROM users 
			WHERE username LIKE 'User_%'
			ORDER BY id
			""")
	return cursor.fetchall()


def add_new_user(new_username, new_password):
	connection = pymysql.connect(host=c.HOST, user=c.USERNAME, password=c.PASSWORD)
	cursor = connection.cursor(pymysql.cursors.DictCursor)
	cursor.execute("""USE movies_DB""")
	try:
		print(new_username)
		print(new_password)
		cursor.execute("""
		INSERT INTO users(username, password) VALUES (%s, %s)
		""", (new_username, new_password))
		connection.commit()

		cursor.execute("""
		    SELECT * FROM users
		    WHERE username = %s
	    	""", (new_username, ))
		return cursor.fetchone()['id']

	except Exception as e:
		# print(e)
		# st.warning('This username already exist. Try logging in or chosing a diferent username')
		# print(e) 	
		return False

def check_data(new_username, new_password):
	cursor = connect_db()
	try:
	  cursor.execute("""
	    SELECT id FROM users
	    WHERE username = %s
	    AND password = %s
	    """, (new_username, new_password))
	  return cursor.fetchone()['id']

	except Exception as e:
	  #st.warning('The combination username/password is not in the database')
	  # print(e) 	
	  return False

def testing_collaborative(selected_genre, years, images_per_page, offset, user_id, mode='test'):

	options = ['View list of liked movies', 'Get recommendations', 'Rate more movies']
	radio_mode = st.radio('Alternate modes', options )

	if radio_mode == options[0]:

		movies_db = get_movies(selected_genre, years, images_per_page, offset, user_id)
		
		scores = [f"Score: {movie['scores']}" for movie in movies_db]
		titles = [movie['title'] for movie in movies_db]
		ids = [movie['id'] for movie in movies_db]
		ratings = [movie['rating'] for movie in movies_db]
		links = [f"{c.MOVIE_DB_URL}{movie['poster_path']}" if movie['poster_path'] is not None else c.NO_IMAGE for movie in movies_db ]
		if ids:
			if selected_genre != 'ALL':
				st.markdown(f"## **Showing list of your rated {selected_genre} movies between {years[0]} - {years[1]}**")
				st.write(f"Currently seeing movies from {images_per_page*offset+1} to {images_per_page*(offset+1)}. Use the commands in the sidebar to see more.")
			else:
				st.markdown(f"## **Showing list of your rated movies between {years[0]} - {years[1]}**")
				st.write(f"Currently seeing movies from {images_per_page*offset+1} to {images_per_page*(offset+1)}. Use the commands in the sidebar to see more.")

			components = display_movies(ids, links, titles, scores, ratings)
		else:
			st.write('Empty list')

	if radio_mode == options[1]:

		cursor = connect_db()
		ratings, user_id_dict, tot_users, tot_movies = cm.get_ratings(cursor)
		# inverse_user_id_dict = {v: k for k,v in user_id_dict.items()}

		try:
			with open(f"{c.current_dir}/data/collaborative_model.pkl", 'rb') as infile:
				container = pickle.load(infile)
				embeddings_users, embeddings_movies = container[0], container[1]
				st.write('Collaborative model embeddings successfully loaded')

			if (len(embeddings_users) != tot_users) | (len(embeddings_movies) != tot_movies):
				st.write('Recomputing collaborative model embeddings')
				
				model = cm.build_regularized_model( ratings,  user_id_dict, tot_users, tot_movies,
				    regularization_coeff=0.4, gravity_coeff=0, embedding_dim=35,
				    init_stddev=.01)
				model.train(num_iterations=1500, learning_rate=10)

				embeddings_users, embeddings_movies = model.embeddings["user_id"], model.embeddings["movie_id"]
				with open(f"{c.current_dir}/data/collaborative_model.pkl", 'wb') as outfile:
					pickle.dump([ embeddings_users, embeddings_movies ], outfile, pickle.HIGHEST_PROTOCOL)

			#print('Loaded similarity matrix')
		except Exception as e:
			st.write('Computing collaborative model embeddings')
			model = cm.build_regularized_model( ratings,  user_id_dict, tot_users, tot_movies,
				    regularization_coeff=0.4, gravity_coeff=0, embedding_dim=35,
				    init_stddev=.01)
			model.train(num_iterations=1500, learning_rate=10)

			embeddings_users, embeddings_movies = model.embeddings["user_id"], model.embeddings["movie_id"]
			with open(f"{c.current_dir}/data/collaborative_model.pkl", 'wb') as outfile:
				pickle.dump([ embeddings_users, embeddings_movies], outfile, pickle.HIGHEST_PROTOCOL)

		scores = cm.compute_scores(embeddings_users[user_id_dict[user_id]], embeddings_movies)
		
		(ids, links, titles, scores) = get_movies_collab_based(scores, years, images_per_page, offset)
		display_movies(ids, links, titles, scores)

	if radio_mode == options[2]:
		if mode == 'test':
			st.write('This option is disabled as you are using a predefined test-user. Create a new user to personalize your ratings.')
		else:
			all_movies = get_movies(selected_genre, years, images_per_page, offset)
		
			scores = [f"Score: {movie['scores']}" for movie in all_movies]
			titles = [movie['title'] for movie in all_movies]
			ids = [movie['id'] for movie in all_movies]
			links = [f"{c.MOVIE_DB_URL}{movie['poster_path']}" if movie['poster_path'] is not None else c.NO_IMAGE for movie in all_movies ]

			rated_movies = get_movies(selected_genre, years, 1000, 0, user_id)
			rated_ids = [movie['id'] for movie in rated_movies]
			user_ratings = [movie['rating'] for movie in rated_movies]

			st.write(user_ratings)
			st.write(rated_ids)
			ratings = [0]*len(ids)

			for (rated_id, rating) in zip(rated_ids, user_ratings):
				try:
					ratings[ids.index(rated_id)] = rating
				except:
					pass

			st.write(ratings)
			# ratings = [movie['rating'] for movie in movies_db]
			
			components = display_movies(ids, links, titles, scores, ratings)

			# st.write(components)
			connection = pymysql.connect(host=c.HOST, user=c.USERNAME, password=c.PASSWORD)
			cursor = connection.cursor(pymysql.cursors.DictCursor)
			cursor.execute("""USE movies_DB""")

			for  comp in components:
				if components[comp]['slider'] > 0:
					cursor.execute("""
	                     SELECT rating FROM user_ratings
	                     WHERE user_id = %s
	                     AND movie_id = %s 
	                     """, (user_id, comp))
					old_rating = cursor.fetchone()
					if old_rating:
						old_rating = old_rating['rating']
					print('Im here')
					print(f"{comp}-> Fom Rating: {old_rating} to rating: {components[comp]['slider']}")
					if old_rating:
						if old_rating != components[comp]['slider']:
							try:
								cursor.execute("""
				                    UPDATE user_ratings
				                    SET rating = %s
				                    WHERE user_id = %s
				                    AND movie_id = %s 
				                    """, (round(components[comp]['slider']), user_id, comp ))
								print(f"movie {comp} updated to {components[comp]['slider']}")
								connection.commit()	
							except Exception as e:
								print(e)
					else:
						try:
							cursor.execute("""
								INSERT INTO user_ratings(user_id, movie_id, rating) 
								VALUES ( %s, %s, %s)
								""", (user_id, comp, round(components[comp]['slider']) ))
							print("movie added")
							connection.commit()	
						except Exception as e:
							print(e)
					
				# new_rating = components[comp]["col"].slider('User rating', 0, 10, value = ratings[idx], key = comp)
				st.write(f"{components[comp]['title']}: Id {comp} has a new rating of {components[comp]['slider']}")
			# components[m_id]["slider"] = components[m_id]["col"].slider('User rating', 0, 10, value = ratings[idx], key = m_id)

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


def display_movies(ids, links, titles, scores, *ratings):
	components = dict()
	prev_id = 0
	if ratings:
		ratings = ratings[0]
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
		components[m_id]["col"].write(f"**{title[0:50] }**  \n\n ({score})")
		#components[m_id]["col"].write(f"{components[m_id]["title"]} | {components[m_id]["score"]}")
		components[m_id]["col"].image(components[m_id]["link"], width=180)
		if ratings:
			components[m_id]["slider"] = components[m_id]["col"].slider('User rating', 0, 10, value = ratings[idx], key = m_id)
	return components

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

	# with open(f"{c.current_dir}/data/cos_sim_matrix.pkl", 'wb') as outfile:
	# 	pickle.dump(cos_sim, outfile, pickle.HIGHEST_PROTOCOL)
	for idx in range(len(cos_sim)):
		np.save(f"{c.current_dir}/data/cos_sim_matrix_{idx}.npy", cos_sim[idx])

	# return cos_sim


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
		features = f'{(director + " ")*3}{" ".join(actors)} {" ".join(genres)} {" ".join(keywords)}' 
		movie_features.append(features)
		count += 1
		computing_bar.progress(round(count/total_movies*100))
	compute_cosine_similarity(movie_features)
	# return compute_cosine_similarity(movie_features)


def get_movies_content_based(cos_scores, years, images_per_page, offset):

	# SORT THE SCORES ACCORDING TO SIMILARITY TO REFERENCED MOVIE
	

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
	msk = [movie['id']-1 for movie in movies]
	cos_scores = list(np.array(cos_scores)[msk])
	cos_scores = list(enumerate(cos_scores))

	sorted_scores = sorted(cos_scores, key=lambda x: x[1], reverse=True)
	
	movie_indexes = [score[0] for score in sorted_scores ][1:]
	# print(time.time()-t)



	# COMPONENTS
	scores, titles, ids, links = [], [], [], []
	for idx in range(images_per_page*offset,images_per_page*(offset+1)):

		try:
			movie_idx = movie_indexes[idx]
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

def get_movies_collab_based(sim_scores, years, images_per_page, offset):

	# SORT THE SCORES ACCORDING TO SIMILARITY TO REFERENCED MOVIE
	cursor = connect_db()

	cursor.execute(""" SELECT DISTINCT(id), title, poster_path, scores
			FROM movies
			-- WHERE YEAR(release_date) >= %s 
			-- AND YEAR(release_date) <= %s 
			ORDER BY id
			""") 
	# , (str(years[0]), str(years[1])))

	movies = cursor.fetchall()


	# Eliminate from movie_indexes, the movies that do not fall in the time range
	# msk = [movie['id']-1 for movie in movies]
	# cos_scores = list(np.array(sim_scores)[msk])
	cos_scores = list(enumerate(sim_scores))
	# sorted_scores_idx = np.argsort(scores)[::-1]
	sorted_scores = sorted(cos_scores, key=lambda x: x[1], reverse=True)
	
	movie_indexes = [score[0] for score in sorted_scores ][0:]
	# print(time.time()-t)



	# COMPONENTS
	scores, titles, ids, links = [], [], [], []
	for idx in range(images_per_page*offset,images_per_page*(offset+1)):

		try:
			movie_idx = movie_indexes[idx]
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

