import sqlite3, pymysql
import config as c
import pandas as pd
import helpers as h


connection = pymysql.connect(host=c.HOST, user=c.USERNAME, password=c.PASSWORD)
cursor = connection.cursor(pymysql.cursors.DictCursor)
cursor.execute("""USE movies_DB""")

# Read movies from CSV file
user_ratings = pd.read_csv(c.DATA_PATH + 'ratings_small.csv', low_memory = False)
links = pd.read_csv(c.DATA_PATH + 'links.csv', low_memory = False)

# TABLE FOR USERS
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(20)
        )
    """);

# Relational table USER_MOVIE_RATING
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_ratings(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        movie_id INT NOT NULL,
        rating INT,
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """);

connection.commit()
count = 0
for idx, user_rating in user_ratings.iterrows():

    # if idx< 1000:
        user_id = user_rating['userId']
        try:
            movieDB_id = links[links['movieId']==user_rating['movieId']]['tmdbId'].values[0]
            rating = user_rating['rating']

            username = f"User_{int(user_id)}"
            password = None

            if idx%1000 == 0:
                print(f"{idx} of {len(user_ratings)}, {count} skipped")

            cursor.execute("""
                INSERT IGNORE INTO users(username, password) VALUES (%s, %s)
                """, (username, password))

            try:
                cursor.execute("""
                    INSERT INTO user_ratings(user_id, movie_id, rating) 
                    VALUES (
                    (SELECT id FROM users WHERE username = %s),
                    (SELECT id FROM movies WHERE movieDB_id = %s),
                     %s)
                    """, (username, movieDB_id, round(rating*2) ))
            except Exception as e:
                count += 1
                # print(e)
                # print(f"{user_rating['movieId']}: {movieDB_id}")
        except Exception as e2:
            count += 1
            # print(e2)
            # print(f"{user_rating['movieId']}")
connection.commit()
  