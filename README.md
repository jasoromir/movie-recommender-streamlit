
# Movie Recommender System

RUNNING AT: [http://35.180.50.126:8501/](http://35.180.50.126:8501/)

## Description

Usually, when I go on Youtube I like to find videos related to Data Science or Deep Learning that I have not seen before.
However, sporadically I like to find songs, humoristic videos or even watch some matches of professional League of Legends.
The problem with this is that Youtube would start recommending me music or videogames clips in which I am not really interested.

Then, one night in bed I had a great idea "What if I could create a recommendation system, with different clusters and only see recommendations of the cluster I am interested in". 

Next day, I checked on Youtube and that option was already implemented, but since I don't use the platform that much I had not been aware of it.

Anyway, I wanted to test my idea, so I decided to build that system myself. As a proof of concept, instead of using the Youtube database, I will implement it using the MovieLens Dataset, that can be downloaded from Kaggle.

[-> Link to download dataset from Kaggle <-](https://www.kaggle.com/rounakbanik/the-movies-dataset?select=ratings.csv)

**NOTE:** Yes, I know! If you visit the projects at Kaggle there are hundreds of repeated implementations of the same EDA processes and the same methods for recommendations using this dataset. THis project aims to be more unique and personalized using other methods and a web user interface using ["streamlit"](https://streamlit.io/)

![App interface](/images/display.png "Display APP")

(CURRENTLY IT WORKS LOCALLY, WORKING ON DEPLOYMENT)


### About the dataset

>The dataset consists of movies released on or before July 2017. Data points include cast, crew, plot keywords, budget, revenue, posters, release dates, languages, production companies, countries, TMDB vote counts and vote averages.
>This dataset also has files containing 26 million ratings from 270,000 users for all 45,000 movies. Ratings are on a scale of 1-5 and have been obtained from the official GroupLens website.


### Table of Contents
**[Description](#description)**<br>
**[Installation](#installation)**<br>
**[Usage Instructions](#usage-instructions)**<br>


---

## Installation


Streamlit -> Display the app (working on deployment)  
SQLite3 -> For easier and faster access to the database  
BeautifulSoup -> Parsing data from the web  

````python
pip install -r requirements.txt 
pip3 install -r requirements.txt
````
## Usage Instructions
### Types of recommendations

![App interface Lord of the rings](/images/content_recom.png "Display APP movies similar to LoTR")

* **Content-based recommenders:** suggest similar items based on a particular item. This system uses item metadata, such as genre, director, description, actors, etc. for movies, to make these recommendations. The general idea behind these recommender systems is that if a person likes a particular item, he or she will also like an item that is similar to it. And to recommend that, it will make use of the user's past item metadata. A good example could be YouTube, where based on your history, it suggests you new videos that you could potentially watch.


* **Collaborative filtering engines:** these systems are widely used, and they try to predict the rating or preference that a user would give an item-based on past ratings and preferences of other users. Collaborative filters do not require item metadata like its content-based counterparts.


* **Simple recommenders:** offer generalized recommendations to every user, based on movie popularity and/or genre. The basic idea behind this system is that movies that are more popular and critically acclaimed will have a higher probability of being liked by the average audience. An example could be IMDB Top 250.




