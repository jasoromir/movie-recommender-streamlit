from config import config as c 
from utils import helpers as h
import numpy as np
import streamlit as st

# Recomendation filter based in metadata to compute similarity among the items(movies) of the dataset
# Here, we will use: TITLE; GENRE, DIRECTOR, ACTORS, KEYWORDS
@st.cache(suppress_st_warning=True)
def get_cos_sim(num_movies, movie_idx):
	try:
		# with open(f"{c.current_dir}/data/cos_sim_matrix.pkl", 'rb') as infile:
		# 	cos_sim = pickle.load(infile) 
		cos_sim = np.load(f"{c.current_dir}/data/cos_sim_matrix_{movie_idx}.npy")

		# if len(cos_sim) != num_movies:
		# 	st.write('Recomputing similarity matrix')
		# 	cos_sim = h.compute_sim_mat()

		#print('Loaded similarity matrix')
	except Exception as e:
		st.write('Computing similarity matrix')
		# cos_sim = h.compute_sim_mat()
		h.compute_sim_mat()
		cos_sim = np.load(f"{c.current_dir}/data/cos_sim_matrix_{movie_idx}.npy")
	return cos_sim

def get_recommendations(movie_idx, years, images_per_page, offset):

	cursor = h.connect_db()
	cursor.execute(""" SELECT COUNT(*) as num_movies FROM movies""");
	num_movies = cursor.fetchone()['num_movies']

	cos_scores = get_cos_sim(num_movies, movie_idx-1)
	# cos_sim = get_cos_sim(num_movies)
	# cos_scores = cos_sim[movie_idx-1][:]

	# GET MOVIES TO RECOMMEND
	(ids, links, titles, scores) = h.get_movies_content_based(cos_scores, years, images_per_page, offset)

	
	# DISPLAY MOVIES
	components = h.display_movies(ids, links, titles, scores)


