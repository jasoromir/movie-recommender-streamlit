import sqlite3
import config as c
import pandas as pd
import helpers as h


# Establish connection with our database
connection = sqlite3.connect(c.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# Recompute the Score based on a weighted metric
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


#cursor.execute("""ALTER TABLE movies ADD COLUMN scores3""")

# for idx, score in zip(ids,scores):
# 	cursor.execute("""UPDATE movies SET scores = ? WHERE id = ?""", (round(score,2),idx))

# connection.commit()

