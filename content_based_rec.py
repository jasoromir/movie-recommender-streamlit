import config as c 
import helpers as h
import numpy as np
import streamlit as st

# Recomendation filter based in metadata to compute similarity among the items(movies) of the dataset
# Here, we will use: TITLE; GENRE, DIRECTOR, ACTORS, KEYWORDS
def get_cos_sim():
	try:
		cos_sim = np.load(f"{c.current_dir}/data/cos_sim_matrix.npy")
		#print('Loaded similarity matrix')
	except Exception as e:
		st.write('Computing similarity matrix')
		cos_sim = h.compute_sim_mat()
	return cos_sim

def get_recommendations(movie_idx, years, images_per_page, offset):

	cos_sim = get_cos_sim()
	cos_scores = cos_sim[movie_idx-1][:]
	cos_scores = list(enumerate(cos_scores))

	sorted_scores = sorted(cos_scores, key=lambda x: x[1], reverse=True)

	# GET MOVIES TO RECOMMEND
	(ids, links, titles, scores) = h.get_movies_content_based(sorted_scores, years, images_per_page, offset)

	
	# DISPLAY MOVIES
	components = h.display_movies(ids, links, titles, scores)


