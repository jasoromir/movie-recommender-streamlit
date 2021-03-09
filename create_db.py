import sqlite3, config

# OPEN or CREATE database
connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

# Table for MOVIES
cursor.execute("""
	CREATE TABLE IF NOT EXISTS movies(
		id INTEGER PRIMARY KEY,
		movieDB_id INTEGER NOT NULL UNIQUE,
		title TEXT NOT NULL UNIQUE,
		duration NOT NULL,
		vote_counts INTEGER NOT NULL,
		vote_average NOT NULL,
		release_date NOT NULL,
		poster_path,
		popularity NOT NULL,
		director NOT NULL
		)
	""")

# Table for ACTORS
cursor.execute("""
	CREATE TABLE IF NOT EXISTS actors(
		id INTEGER PRIMARY KEY,
		name NOT NULL UNIQUE
		)
	""")

# Table for GENRES
cursor.execute("""
	CREATE TABLE IF NOT EXISTS genres(
		id INTEGER PRIMARY KEY,
		name NOT NULL UNIQUE
		)
	""")

# Relational table MOVIE-GENRE
cursor.execute("""
	CREATE TABLE IF NOT EXISTS movie_genres(
		id INTEGER PRIMARY KEY,
		movie_id INTEGER NOT NULL,
		genre_id INTEGER NOT NULL,
		FOREIGN KEY (movie_id) REFERENCES movies (id)
		FOREIGN KEY (genre_id) REFERENCES genres (id)
		)
	""")

# Relational table MOVIE-ACTOR
cursor.execute("""
	CREATE TABLE IF NOT EXISTS movie_actors(
		id INTEGER PRIMARY KEY,
		movie_id INTEGER NOT NULL,
		actor_id INTEGER NOT NULL,
		FOREIGN KEY (movie_id) REFERENCES movies (id)
		FOREIGN KEY (actor_id) REFERENCES actors (id)
		)
	""")

# Table for KEYWORDS
cursor.execute("""
	CREATE TABLE IF NOT EXISTS keywords(
		id INTEGER PRIMARY KEY,
		name NOT NULL UNIQUE
		)
	""")

# Relational table MOVIE-KEYWORD
cursor.execute("""
	CREATE TABLE IF NOT EXISTS movie_keywords(
		id INTEGER PRIMARY KEY,
		movie_id INTEGER NOT NULL,
		keyword_id INTEGER NOT NULL,
		FOREIGN KEY (movie_id) REFERENCES movies (id)
		FOREIGN KEY (keyword_id) REFERENCES keywords (id)
		)
	""")


# Commit changes to the database
connection.commit()