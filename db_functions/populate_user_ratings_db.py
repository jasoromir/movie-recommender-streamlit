
from config import config as c
import pymysql
import pandas as pd

def populate(connection, cursor):

    # Read movies from CSV file
    user_ratings = pd.read_csv(c.DATA_PATH + 'ratings_small.csv', low_memory = False)
    links = pd.read_csv(c.DATA_PATH + 'links.csv', low_memory = False)

    count = 0
    for idx, user_rating in user_ratings.iterrows():
        user_id = user_rating['userId']

        try:
            movieDB_id = links[links['movieId']==user_rating['movieId']]['tmdbId'].values[0]
            rating = user_rating['rating']
            username = f"User_{int(user_id)}"
            password = None

            # DEBUGGING: PRINT NUMBER OF USER RATINGS
            # if idx%1000 == 0:
            #     print(f"{idx} of {len(user_ratings)}, {count} skipped")


            # ADD USER TO THE DATABASE
            cursor.execute("""
                INSERT IGNORE INTO users(username, password) VALUES (%s, %s)
                """, (username, password))


            # SKIP RATING IF THE MOVIE IS NOT IN THE DATABASE
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

        except Exception as e2:
            count += 1
            # print(e2)

    connection.commit()
      