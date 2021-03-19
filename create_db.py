import sqlite3, config
import pymysql



connection = pymysql.connect(host=c.HOST, user=c.USERNAME, password=c.PASSWORD)
cursor = connection.cursor(pymysql.cursors.DictCursor)

cursor.execute("""CREATE DATABASE IF NOT EXISTS movies_DB""")
cursor.execute("""USE movies_DB""")


cursor.execute("""
	CREATE TABLE IF NOT EXISTS movies(
    id INT AUTO_INCREMENT PRIMARY KEY,
    movieDB_id INT NOT NULL UNIQUE,
    title VARCHAR(100) NOT NULL UNIQUE,
    duration VARCHAR(20) NOT NULL,
    vote_counts INT NOT NULL,
    vote_average DECIMAL(3,2) NOT NULL,
    release_date DATE NOT NULL,
    poster_path TEXT,
    popularity DECIMAL(6,2) NOT NULL,
    director VARCHAR(50) NOT NULL
		)""");

# Table for ACTORS
cursor.execute("""
	CREATE TABLE IF NOT EXISTS actors(
		id INT AUTO_INCREMENT PRIMARY KEY,
		name VARCHAR(50) NOT NULL UNIQUE
		)
	""");

# Table for GENRES
cursor.execute("""
	CREATE TABLE IF NOT EXISTS genres(
		id INT AUTO_INCREMENT PRIMARY KEY,
		name VARCHAR(50) NOT NULL UNIQUE
		)
	""");

# Relational table MOVIE-GENRE
cursor.execute("""
	CREATE TABLE IF NOT EXISTS movie_genres(
		id INT AUTO_INCREMENT PRIMARY KEY,
		movie_id INT NOT NULL,
		genre_id INT NOT NULL,
		FOREIGN KEY (movie_id) REFERENCES movies (id),
		FOREIGN KEY (genre_id) REFERENCES genres (id)
		)
	""");

# Relational table MOVIE-ACTOR
cursor.execute("""
	CREATE TABLE IF NOT EXISTS movie_actors(
		id INT AUTO_INCREMENT PRIMARY KEY,
		movie_id INT NOT NULL,
		actor_id INT NOT NULL,
		FOREIGN KEY (movie_id) REFERENCES movies (id),
		FOREIGN KEY (actor_id) REFERENCES actors (id)
		)
	""");

# Table for KEYWORDS
cursor.execute("""
	CREATE TABLE IF NOT EXISTS keywords(
		id INT AUTO_INCREMENT PRIMARY KEY,
		name VARCHAR(50) NOT NULL UNIQUE
		)
	""");

# Relational table MOVIE-KEYWORD
cursor.execute("""
	CREATE TABLE IF NOT EXISTS movie_keywords(
		id INT AUTO_INCREMENT PRIMARY KEY,
		movie_id INT NOT NULL,
		keyword_id INT NOT NULL,
		FOREIGN KEY (movie_id) REFERENCES movies (id),
		FOREIGN KEY (keyword_id) REFERENCES keywords (id)
		)
	""");


connection.commit()


# # OPEN or CREATE database
# connection = sqlite3.connect(config.DB_FILE)

# cursor = connection.cursor()

# # Table for MOVIES
# cursor.execute("""
# 	CREATE TABLE IF NOT EXISTS movies(
# 		id INTEGER PRIMARY KEY,
# 		movieDB_id INTEGER NOT NULL UNIQUE,
# 		title TEXT NOT NULL UNIQUE,
# 		duration NOT NULL,
# 		vote_counts INTEGER NOT NULL,
# 		vote_average NOT NULL,
# 		release_date NOT NULL,
# 		poster_path,
# 		popularity NOT NULL,
# 		director NOT NULL
# 		)
# 	""")

# # Table for ACTORS
# cursor.execute("""
# 	CREATE TABLE IF NOT EXISTS actors(
# 		id INTEGER PRIMARY KEY,
# 		name NOT NULL UNIQUE
# 		)
# 	""")

# # Table for GENRES
# cursor.execute("""
# 	CREATE TABLE IF NOT EXISTS genres(
# 		id INTEGER PRIMARY KEY,
# 		name NOT NULL UNIQUE
# 		)
# 	""")

# # Relational table MOVIE-GENRE
# cursor.execute("""
# 	CREATE TABLE IF NOT EXISTS movie_genres(
# 		id INTEGER PRIMARY KEY,
# 		movie_id INTEGER NOT NULL,
# 		genre_id INTEGER NOT NULL,
# 		FOREIGN KEY (movie_id) REFERENCES movies (id)
# 		FOREIGN KEY (genre_id) REFERENCES genres (id)
# 		)
# 	""")

# # Relational table MOVIE-ACTOR
# cursor.execute("""
# 	CREATE TABLE IF NOT EXISTS movie_actors(
# 		id INTEGER PRIMARY KEY,
# 		movie_id INTEGER NOT NULL,
# 		actor_id INTEGER NOT NULL,
# 		FOREIGN KEY (movie_id) REFERENCES movies (id)
# 		FOREIGN KEY (actor_id) REFERENCES actors (id)
# 		)
# 	""")

# # Table for KEYWORDS
# cursor.execute("""
# 	CREATE TABLE IF NOT EXISTS keywords(
# 		id INTEGER PRIMARY KEY,
# 		name NOT NULL UNIQUE
# 		)
# 	""")

# # Relational table MOVIE-KEYWORD
# cursor.execute("""
# 	CREATE TABLE IF NOT EXISTS movie_keywords(
# 		id INTEGER PRIMARY KEY,
# 		movie_id INTEGER NOT NULL,
# 		keyword_id INTEGER NOT NULL,
# 		FOREIGN KEY (movie_id) REFERENCES movies (id)
# 		FOREIGN KEY (keyword_id) REFERENCES keywords (id)
# 		)
# 	""")


# # Commit changes to the database
# connection.commit()