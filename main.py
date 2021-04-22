
#import functions from folders
from config import config as c
from utils import helpers as h
from utils import content_based_rec

# import libraries
import streamlit as st
import pandas as pd 
import numpy as np 
import time
from ast import literal_eval
# import sqlite3


# PAGE TITLE
st.set_page_config(page_title="Movie Recommender", layout='wide')
st.title('Movies Recomender with Streamlit')


# GENRE SELECT
genres = h.get_genres_for_display()
selected_genre = st.sidebar.selectbox('Select Genre', sorted(genres), index = 0)


# YEAR SLIDER
oldest, newest = h.get_movie_range()
years = st.sidebar.slider('Movies between:', int(oldest), int(newest), (int(oldest), int(newest)))


# GADGETS TO DISPLAY MOVIES
images_per_page = st.sidebar.slider('Images per page', 5, 60, value = 30, step = 5)
offset = st.sidebar.slider(f"<- Navigate through pages ->", 0, 10, value = 0, step = 1)


# RECOMMENDATION METHOD
rec_method = h.get_recommendation_method()
if rec_method == 'Generalized recommendations':

	# DISPLAY SELECTION
	if selected_genre != 'ALL':
		st.markdown(f"## **List of Best {selected_genre} Movies between {years[0]} - {years[1]}**")
	else:
		st.markdown(f"## **List of Best Movies between {years[0]} - {years[1]}**")

	# GET MOVIES TO RECOMMEND
	movies_db = h.get_movies(selected_genre, years, images_per_page, offset)

	# COMPONENTS
	scores = [f"Score: {movie['scores']}" for movie in movies_db]
	titles = [movie['title'] for movie in movies_db]
	ids = [movie['id'] for movie in movies_db]
	links = [f"{c.MOVIE_DB_URL}{movie['poster_path']}" if movie['poster_path'] is not None else c.NO_IMAGE for movie in movies_db ]


	# DISPLAY MOVIES
	components = h.display_movies(ids, links, titles, scores)


elif rec_method == 'Content-based recommendations':
	name_like = st.sidebar.text_input("Recommend movies like:", 'Title starts like...')
	searched = h.search_movie(name_like)

	movies_titles = [search['title'] for search in searched]
	movies_idx = [search['id'] for search in searched]
	movie_links = [search['poster_path'] for search in searched]

	movie_name = st.sidebar.selectbox('', movies_titles)
	try:
		movie_id = movies_idx[movies_titles.index(movie_name)]
		st.sidebar.image(f"{c.MOVIE_DB_URL}{movie_links[movies_titles.index(movie_name)]}")
		st.markdown(f"## **List of Movies similar to {movie_name} between {years[0]} - {years[1]}**")

		content_based_rec.get_recommendations(movie_id, years, images_per_page, offset)
	except Exception as e:
		st.markdown(f"## **Search for a movie in the Sidebar**")
		st.success("Waiting for a movie...")
		#st.write(e)

elif rec_method == 'Collaborative recomendations':

	usernames = h.get_usernames()
	user_ids =  [item['id'] for item in usernames]
	usernames = [item['username'] for item in usernames]
	
	# checkbox_help = f"Unselect this checkbox if you want to go back and chose a diferent user or register a new user"
	user_options = ['Choose/Rechoose', 'Test-users', 'New user', 'Log in']
	radio_options = st.sidebar.empty()
	user_option = radio_options.radio('Logged_in', user_options,  0)

	try:
		# GET MOVIES TO RECOMMEND
		h.testing_collaborative(selected_genre, years, images_per_page, offset, user_id)
		
	except:
		if user_option == user_options[0]:
			title_description = f"## **Are you a new user?**"
			st.markdown(title_description)

			info_description = (f"## **OPTIONS:** \n " + 
				f" 1) Choose a 'test-user' from the sidebar to see their preferred movies and recommendations \n\n" +  
				f" 2) Create a new-user or log in to input your preferences and get personalized recommendations")
			st.info(info_description)

		elif user_option == user_options[1]:
			user_name = st.sidebar.selectbox('Select a test-user', usernames)
			
			# test_user_button = st.sidebar.button('Choose test user')
			# if test_user_button:
			user_id = user_ids[usernames.index(user_name)]
			st.success(f"You have selected {user_name}. Now you can view his list of liked movies and his recommendations")
			time.sleep(2)
			h.testing_collaborative(selected_genre, years, images_per_page, offset, user_id, 'test')
		else:
			new_username = st.sidebar.text_input("Introduce your username:", 'username')
			new_password = st.sidebar.text_input("Introduce your password:", 'password')
			if user_option == user_options[2]:
				
				new_user_button = st.sidebar.button('Create new user')
				if new_user_button:
					try:
						user_id = h.add_new_user(new_username, new_password)	
						user_name = new_username
						if user_id:
							st.success(f"Hello {user_name}! Your account have been successfully created")
							time.sleep(2)
							user_option = radio_options.radio('Logged_in', user_options, 3)
					except:
						st.warning('This username already exist. Try logging in or chosing a diferent username')

			if user_option == user_options[3]:

				user_id = h.check_data(new_username, new_password)
				if user_id:
					user_name = new_username
					st.success(f"Hello {user_name}! Your are now logged in")
					time.sleep(2)
					h.testing_collaborative(selected_genre, years, images_per_page, offset, user_id, 'real')
				else:
					st.warning("This username and password combination do not exist in the data base")

		
	

	




