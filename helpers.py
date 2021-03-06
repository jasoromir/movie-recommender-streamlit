import config as c
import requests
from bs4 import BeautifulSoup


def get_poster_path(movie_id):
	r = requests.get(f"{c.MOVIE_DB_URL}movie/{movie_id}")
	soup = BeautifulSoup(r.content)
	for item in soup.findAll('meta'):
		if str(item).split()[1].endswith('.jpg"'):
			return (str(item).split()[1].strip('content=').strip('"'))


def weighted_rating(df, m = 0, C = 0):
	""" COMPUTE WEIGHTED AVERAGE USING THE FORMULA:
		(v/(v+m) * R) + (m/(v+m) * C)
		v is the number of votes for the movie
		m is the minimum votes required to be listed in the chart
		R is the average rating of the movie
		C is the mean vote across the whole report
	"""

	vote = df['vote_count']
	vote_average = df['vote_average']

	return ((vote/(vote+m) * vote_average)
	    +  (m/(vote + m) * C))