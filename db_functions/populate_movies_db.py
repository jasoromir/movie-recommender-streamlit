
from utils import helpers as h
from config import config as c

import pymysql
import pandas as pd

def populate(connection, cursor):

  # READ MOVIES FROM CSV AND RETAIN THE 30% MOST VOTED
  movies = pd.read_csv(c.DATA_PATH + 'movies_metadata.csv', low_memory = False)
  most_voted = movies['vote_count'].quantile(0.70)
  most_voted_movies = movies.loc[movies['vote_count'] >= most_voted]

  # READ ACTORS, DIRECTOR AND KEYWORDS FROM CSV
  credits = pd.read_csv(c.DATA_PATH + 'credits.csv', low_memory = False)
  keywords_df = pd.read_csv(c.DATA_PATH + 'keywords.csv')


  # ITERATE THROUGH ALL THE MOVIES AND STORE THEM IN A DATABASE FOR EASIER ACCESS
  count = 0
  total = len(most_voted_movies)
  for idx , movie in most_voted_movies.iterrows():

      # DEBUGGIN: PRINT NUMBER OF PROCESED MOVIES 
      # count += 1
      # print(f"Processing {count} out of {total} movies")

      # GET THE VALUES WE ARE INTERESTED IN
      movieDB_id   = movie['id']
      title        = movie['title']
      duration     = movie['runtime']
      vote_counts  = movie['vote_count']
      vote_average = movie['vote_average']
      release_date = movie['release_date']
      popularity   = movie['popularity']

      # ONLY PROCESS THE REST OF THE METADATA IF THE MOVIE HAS NOT BEEN ALREADY INCLUDED
      cursor.execute("""SELECT * FROM movies WHERE movieDB_id = %s""", (movieDB_id,))
      if cursor.fetchone() is None:

        poster_path = h.get_poster_path(movieDB_id)
        director    = h.get_director(movieDB_id, credits)
        actors      = h.get_main_actors(movieDB_id, credits)
        genres      = h.get_genres(movieDB_id, most_voted_movies)
        keywords    = h.get_keywords(movieDB_id, keywords_df)

        # ADD MOVIE
        try:
          print(f"Adding movie: {title} with ID:{movieDB_id}")
          cursor.execute("""
              INSERT INTO movies (movieDB_id, title, duration, vote_counts, vote_average, 
              release_date, poster_path, popularity, director) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
              """, (movieDB_id, title, duration, vote_counts, vote_average, release_date, poster_path, popularity, director))
        except Exception as e:
              print(f"This movie:{title} already existed")
              # print(e) 
              pass

        # ADD ACTORS       
        for actor in actors:	
            cursor.execute("""INSERT IGNORE INTO actors (name) VALUES (%s)""", (actor,))


        # ADD GENRE
        for genre in genres:	
            cursor.execute("""INSERT IGNORE INTO genres (name) VALUES (%s)""", (genre,))

        # ADD KEYWORDS
        for keyword in keywords:	
            cursor.execute("""INSERT IGNORE INTO keywords (name) VALUES (%s)""", (keyword,))


        try:
          cursor.execute("""SELECT id FROM movies WHERE title = %s """, (title,))
          movie_id = cursor.fetchone()['id']
          for genre in genres:
            cursor.execute("""SELECT id FROM genres WHERE name = %s """, (genre,))
            genre_id = cursor.fetchone()['id']
            cursor.execute("""
                INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s,%s)
                """, (movie_id,genre_id))

          for actor in actors:
            cursor.execute("""SELECT id FROM actors WHERE name = %s""", (actor,))
            actor_id = cursor.fetchone()['id']
            cursor.execute("""
                INSERT INTO movie_actors (movie_id, actor_id) VALUES (%s,%s)
                """, (movie_id,actor_id))

          for keyword in keywords:
            cursor.execute("""SELECT id FROM keywords WHERE name = %s""", (keyword,))
            keyword_id = cursor.fetchone()['id']
            cursor.execute("""
                INSERT INTO movie_keywords (movie_id, keyword_id) VALUES (%s,%s)
                """, (movie_id,keyword_id))	

        except Exception as e:
          pass

  connection.commit()  


def add_scores(connection, cursor):
  cursor.execute("""SELECT id, vote_counts, vote_average FROM movies""")
  movies = cursor.fetchall()

  ids = [movie['id'] for movie in movies]
  vote_counts = [int(float(movie['vote_counts'])) for movie in movies]
  vote_average = [float(movie['vote_average']) for movie in movies]

  scores = h.weighted_rating(vote_counts, vote_average)
  cursor.execute("""ALTER TABLE movies ADD scores DECIMAL(3,2) NOT NULL""")

  for idx, score in zip(ids,scores):
    cursor.execute("""UPDATE movies SET scores = %s WHERE id = %s""", (score,idx))

  connection.commit()

  #cursor.execute("""ALTER TABLE movies DROP COLUMN scores""")




# ======================================================
# ============== OLD COLDE USING SQLITE ================
# ======================================================

# # Establish connection with our database
# connection = sqlite3.connect(c.DB_FILE)

# connection.row_factory = sqlite3.Row

# # Read movies from CSV file
# movies = pd.read_csv(c.DATA_PATH + 'movies_metadata.csv', low_memory = False)
# # 10% most voted movies
# most_voted = movies['vote_count'].quantile(0.9)
# most_voted_movies = movies.loc[movies['vote_count'] >= most_voted]

# credits = pd.read_csv(c.DATA_PATH + 'credits.csv', low_memory = False)
# keywords_df = pd.read_csv(c.DATA_PATH + 'keywords.csv')


# cursor = connection.cursor()

# for idx , movie in most_voted_movies.iterrows():

# 		movieDB_id = movie['id']
# 		title = movie['title']
# 		duration = movie['runtime']
# 		vote_counts = movie['vote_count']
# 		vote_average = movie['vote_average']
# 		release_date = movie['release_date']
# 		popularity = movie['popularity']
# 		poster_path = h.get_poster_path(movieDB_id)
# 		director = h.get_director(movieDB_id, credits)
# 		actors = h.get_main_actors(movieDB_id, credits)
# 		genres = h.get_genres(movieDB_id, most_voted_movies)
# 		keywords = h.get_keywords(movieDB_id, keywords_df)

# 		print(f"{idx} {title}")
# 		try:
# 			# print(f"Adding movie: {title} with ID:{movieDB_id}")
# 			cursor.execute("""
# 				INSERT INTO movies (movieDB_id, title, duration, vote_counts, vote_average, 
# 				release_date, poster_path, popularity, director) VALUES (?,?,?,?,?,?,?,?,?)
# 				""", (movieDB_id, title, duration, vote_counts, vote_average, release_date, poster_path, popularity, director))

# 		except Exception as e:
# 			# print(f"This movie:{title} already existed")
# 			# print(e) 
# 			pass

# 		for actor in actors:	
# 			try:
# 				# print(f"Adding actor: {actor}")
# 				cursor.execute("""
# 					INSERT INTO actors (name) VALUES (?)
# 					""", (actor,))
# 			except Exception as e:
# 				# print(f"This actor: {actor} already existed")
# 				# print(e) 	
# 				pass

# 		for genre in genres:	
# 			try:
# 				# print(f"Adding genre: {genre}")
# 				cursor.execute("""
# 					INSERT INTO genres (name) VALUES (?)
# 					""", (genre,))
# 			except Exception as e:
# 				# print(f"This genre: {genre} already existed")
# 				# print(e) 	
# 				pass


# 		for keyword in keywords:	
# 			try:
# 				# print(f"Adding genre: {genre}")
# 				cursor.execute("""
# 					INSERT INTO keywords (name) VALUES (?)
# 					""", (keyword,))
# 			except Exception as e:
# 				# print(f"This genre: {genre} already existed")
# 				# print(e) 	
# 				pass


# 		cursor.execute("""SELECT id FROM movies WHERE title == ?""", (title,))
# 		movie_id = cursor.fetchone()[0]
# 		for genre in genres:
# 			cursor.execute("""SELECT id FROM genres WHERE name == ?""", (genre,))
# 			genre_id = cursor.fetchone()[0]

# 			cursor.execute("""
# 					INSERT INTO movie_genres (movie_id, genre_id) VALUES (?,?)
# 					""", (movie_id,genre_id))

# 		for actor in actors:
# 			cursor.execute("""SELECT id FROM actors WHERE name == ?""", (actor,))
# 			actor_id = cursor.fetchone()[0]
# 			cursor.execute("""
# 					INSERT INTO movie_actors (movie_id, actor_id) VALUES (?,?)
# 					""", (movie_id,actor_id))

# 		for keyword in keywords:
# 			cursor.execute("""SELECT id FROM keywords WHERE name == ?""", (keyword,))
# 			keyword_id = cursor.fetchone()[0]
# 			cursor.execute("""
# 					INSERT INTO movie_keywords (movie_id, keyword_id) VALUES (?,?)
# 					""", (movie_id,keyword_id))	

# connection.commit()

