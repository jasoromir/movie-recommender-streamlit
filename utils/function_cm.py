
from config   import config as c
from .CFModel import CFModel
import sklearn
import pymysql
import pandas as pd
import numpy as np
import collections
from sklearn.model_selection import train_test_split
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
tf.logging.set_verbosity(tf.logging.ERROR)


connection = pymysql.connect(host=c.HOST, user=c.USERNAME, password=c.PASSWORD)
cursor = connection.cursor(pymysql.cursors.DictCursor)
#cursor.execute("""USE %s""", (c.DB_NAME,))
cursor.execute("""USE movies_DB""")

def get_ratings(cursor):
	cursor.execute(""" SELECT COUNT(*) AS tot_users FROM users""")
	tot_users = cursor.fetchone()['tot_users']

	cursor.execute(""" SELECT COUNT(*) AS tot_movies FROM movies""")
	tot_movies = cursor.fetchone()['tot_movies']

	cursor.execute(""" SELECT * FROM user_ratings""")
	ratings = cursor.fetchall()

	user_id_dict = dict()
	count = 0
	prev_id = 0
	for item in ratings:
		new_id = item['user_id']
		if new_id != prev_id:
			user_id_dict[new_id] = count
			count += 1
			prev_id = new_id
	return (ratings, user_id_dict, tot_users, tot_movies)


def build_rating_sparse_tensor(ratings, user_id_dict, tot_users, tot_movies):
	"""
	  Returns:
	    a tf.SparseTensor representing the ratings matrix.
	"""
	values = []
	indices = []
	for item in ratings:
		u_id = item['user_id']
		rating = item['rating']
		movie_id = item['movie_id']-1
		user_id = user_id_dict[u_id]
		indices.append([user_id, movie_id]) 
		values.append(rating)

	return tf.SparseTensor(
		indices=indices,
		values=values,
		dense_shape=[tot_users, tot_movies])


def sparse_mean_square_error(sparse_ratings, user_embeddings, movie_embeddings):
	"""
	Args:
	sparse_ratings: A SparseTensor rating matrix, of dense_shape [N, M]
	user_embeddings: A dense Tensor U of shape [N, k] where k is the embedding
	  dimension, such that U_i is the embedding of user i.
	movie_embeddings: A dense Tensor V of shape [M, k] where k is the embedding
	  dimension, such that V_j is the embedding of movie j.
	Returns:
	A scalar Tensor representing the MSE between the true ratings and the
	  model's predictions.
	"""
	reconstructed_ratings = tf.matmul(user_embeddings, movie_embeddings, transpose_b=True)
	# Select values of reconstructed matrix for indexes filled in the original matrix
	predictions = tf.gather_nd(reconstructed_ratings, sparse_ratings.indices)
	loss = tf.losses.mean_squared_error(sparse_ratings.values, predictions)
	return loss


def gravity(U, V):
  """Creates a gravity loss given two embedding matrices."""
  return 1. / (U.shape[0].value*V.shape[0].value) * tf.reduce_sum(
      tf.matmul(U, U, transpose_a=True) * tf.matmul(V, V, transpose_a=True))



def build_regularized_model(
    ratings, user_id_dict, tot_users, tot_movies, embedding_dim=3, regularization_coeff=.1, gravity_coeff=1.,
    init_stddev=0.1):
	"""
	Args:
	ratings: the DataFrame of movie ratings.
	embedding_dim: The dimension of the embedding space.
	regularization_coeff: The regularization coefficient lambda.
	gravity_coeff: The gravity regularization coefficient lambda_g.
	Returns:
	A CFModel object that uses a regularized loss.
	"""

	# Split the ratings DataFrame into train and test.
	train_ratings, test_ratings =  train_test_split(ratings)

	# SparseTensor representation of the train and test datasets.
	A_train = build_rating_sparse_tensor(train_ratings, user_id_dict, tot_users, tot_movies)
	A_test = build_rating_sparse_tensor(test_ratings, user_id_dict, tot_users, tot_movies)
	U = tf.Variable(tf.random_normal(
	[A_train.dense_shape[0], embedding_dim], stddev=init_stddev))
	V = tf.Variable(tf.random_normal(
	[A_train.dense_shape[1], embedding_dim], stddev=init_stddev))

	error_train = sparse_mean_square_error(A_train, U, V)
	error_test = sparse_mean_square_error(A_test, U, V)

	# Loss functions
	gravity_loss = gravity_coeff * gravity(U, V)

	regularization_loss = regularization_coeff * (
		tf.reduce_sum(U*U)/U.shape[0].value + tf.reduce_sum(V*V)/V.shape[0].value)
	total_loss = error_train + regularization_loss + gravity_loss

	losses = {
		'train_error_observed': error_train,
		'test_error_observed': error_test,
		}
	loss_components = {
		'observed_loss': error_train,
		'regularization_loss': regularization_loss,
		'gravity_loss': gravity_loss,
		}
	embeddings = {"user_id": U, "movie_id": V}

	return CFModel(embeddings, total_loss, [losses, loss_components])


def compute_scores(query_embedding, item_embeddings):
  """Computes the scores of the candidates given a query.
  Args:
    query_embedding: a vector of shape [k], representing the query embedding.
    item_embeddings: a matrix of shape [N, k], such that row i is the embedding
      of item i.
  Returns:
    scores: a vector of shape [N], such that scores[i] is the score of item i using COSINE similarity.
  """
  u = query_embedding
  V = item_embeddings
  V = V / np.linalg.norm(V, axis=1, keepdims=True)
  u = u / np.linalg.norm(u)
  scores = u.dot(V.T)
  return scores