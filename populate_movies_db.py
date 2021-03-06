import sqlite3
import config as c
import pandas as pd
import helpers as h

# Establish connection with our database
connection = sqlite3.connect(c.DB_FILE)

connection.row_factory = sqlite3.Row

# Read movies from CSV file
movies = pd.read_csv(c.DATA_PATH + 'movies_metadata.csv', low_memory = False)
credits = pd.read_csv(c.DATA_PATH + 'credits.csv', low_memory = False)

cursor = connection.cursor()

for idx , movie in movies.iterrows():
	if idx < 50:
		movieDB_id = movie['id']
		title = movie['title']
		duration = movie['runtime']
		vote_counts = movie['vote_count']
		vote_average = movie['vote_average']
		release_date = movie['release_date']
		popularity = movie['popularity']
		poster_path = h.get_poster_path(movieDB_id)
		director = 'None' # TO DO

		print(f"Adding movie:{title} with ID:{movieDB_id}")
		cursor.execute("""
			INSERT INTO movies (movieDB_id, title, duration, vote_counts, vote_average, 
			release_date, poster_path, popularity, director) VALUES (?,?,?,?,?,?,?,?,?)
			""", (movieDB_id, title, duration, vote_counts, vote_average, release_date, poster_path, popularity, director))


connection.commit()

