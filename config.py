import os
import secrets

# Database
current_dir = os.getcwd()
DB_FILE = f'{current_dir}/movies_db.db'

DB_NAME = "movies_DB"
USERNAME = secrets.USERNAME
PASSWORD= secrets.PASSWORD
HOST= secrets.HOST
PORT= "3306"

MOVIES_PER_ROW = 5
DATA_PATH = f"{current_dir}/data/"
MOVIE_DB_URL = "https://www.themoviedb.org/"
NO_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Image-missing.svg/480px-Image-missing.svg.png"


rec_methods = ['Generalized recommendations', 'Content-based recommendations', 'Collaborative recomendations']
rec_description = dict()
rec_description['Generalized recommendations'] = "These recommendations are based on movie popularity"
rec_description['Content-based recommendations'] = "Recommend similar movies based on a particular movie."
rec_description['Collaborative recomendations'] = "Recommends movies based on past ratings and preferences of other 'similar' users. (DEVELOPING)"

