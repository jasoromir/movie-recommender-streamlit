import sqlite3
import config as c
import pandas as pd
import helpers as h

# Establish connection with our database
connection = sqlite3.connect(c.DB_FILE)

connection.row_factory = sqlite3.Row

# Read movies from CSV file
movies = pd.read_csv(c.DATA_PATH + 'movies_metadata.csv', low_memory = False)
# 10% most voted movies
most_voted = movies['vote_count'].quantile(0.9)
most_voted_movies = movies.loc[movies['vote_count'] >= most_voted]

credits = pd.read_csv(c.DATA_PATH + 'credits.csv', low_memory = False)

cursor = connection.cursor()

for idx , movie in most_voted_movies.iterrows():

		movieDB_id = movie['id']
		title = movie['title']
		duration = movie['runtime']
		vote_counts = movie['vote_count']
		vote_average = movie['vote_average']
		release_date = movie['release_date']
		popularity = movie['popularity']
		poster_path = h.get_poster_path(movieDB_id)
		director = h.get_director(movieDB_id, credits)
		actors = h.get_main_actors(movieDB_id, credits)
		genres = h.get_genres(movieDB_id, most_voted_movies)

		print(f"{idx} {title}")
		try:
			# print(f"Adding movie: {title} with ID:{movieDB_id}")
			cursor.execute("""
				INSERT INTO movies (movieDB_id, title, duration, vote_counts, vote_average, 
				release_date, poster_path, popularity, director) VALUES (?,?,?,?,?,?,?,?,?)
				""", (movieDB_id, title, duration, vote_counts, vote_average, release_date, poster_path, popularity, director))

		except Exception as e:
			# print(f"This movie:{title} already existed")
			# print(e) 
			pass

		for actor in actors:	
			try:
				# print(f"Adding actor: {actor}")
				cursor.execute("""
					INSERT INTO actors (name) VALUES (?)
					""", (actor,))
			except Exception as e:
				# print(f"This actor: {actor} already existed")
				# print(e) 	
				pass

		for genre in genres:	
			try:
				# print(f"Adding genre: {genre}")
				cursor.execute("""
					INSERT INTO genres (name) VALUES (?)
					""", (genre,))
			except Exception as e:
				# print(f"This genre: {genre} already existed")
				# print(e) 	
				pass


		cursor.execute("""SELECT id FROM movies WHERE title == ?""", (title,))
		movie_id = cursor.fetchone()[0]
		for genre in genres:
			cursor.execute("""SELECT id FROM genres WHERE name == ?""", (genre,))
			genre_id = cursor.fetchone()[0]

			cursor.execute("""
					INSERT INTO movie_genres (movie_id, genre_id) VALUES (?,?)
					""", (movie_id,genre_id))

		for actor in actors:
			cursor.execute("""SELECT id FROM actors WHERE name == ?""", (actor,))
			actor_id = cursor.fetchone()[0]
			cursor.execute("""
					INSERT INTO movie_actors (movie_id, actor_id) VALUES (?,?)
					""", (movie_id,actor_id))


connection.commit()

