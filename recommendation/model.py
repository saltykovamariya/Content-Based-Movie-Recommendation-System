import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsClassifier
from sklearn.metrics.pairwise import pairwise_distances
from random import choice
from random import choices
import random


from sklearn.feature_extraction.text import TfidfVectorizer
import itertools

from sklearn.metrics.pairwise import cosine_similarity
import pickle
import imdb
import lxml
import lxml.html

df_we = pd.read_csv('./recommendation/df_we.csv')
df_links = pd.read_csv('./recommendation/links.csv')
movies = pd.read_csv('./recommendation/movies_df_eddited_1995.csv')
with open('./recommendation/cosine_sim_df.pickle', 'rb') as f:
  cosine_sim_df=pickle.load(f)

top_movies=[608, 1721, 1, 209157, 2]
def recommend(list_names, top=10):
    list_film = []
    list_film2 = []
    need_film = []
    top_list = []
    for i in list_names:
        # получаем список фильмов с пересечениями
        list_film += ([x for x in df_we[df_we["rating"].isin([4, 4.5, 5]) & df_we["user_id"].isin([i])]["movieId"] if
                       x not in top_movies])
    for i in list_film:
        if movies[movies['movieId'].isin([i])].shape[0] > 0:
            list_film2.append(i)

    if len(list_names) > 1:
        list_film = list({x for x in list_film if list_film2.count(x) > 1})
        for i in list_film:
            if movies[movies['movieId'].isin([i])].shape[0] > 0:
                need_film.append(i)
        return need_film
    else:
        return list_film2[:3]

def genre_recommendations(m, M=cosine_sim_df, k=20):
  list_for_all = []
  for i in m:
    ix = M.loc[:,i].to_numpy().argpartition(range(-1,-k,-1))
    closest = M.columns[ix[-1:-(k+2):-1]]
    closest = closest.drop(i, errors='ignore')
    list_for_all+=(choices(list(closest), k=10))
  list_for_all_merge = list({x for x in list_for_all if list_for_all.count(x)>1})
  if len(list_for_all_merge) == 0:
      return list_for_all.append(choice(top_movies), k=5)[:5]

  else:
      if len(list_for_all_merge) == 5:
          return list_for_all_merge
      if len(list_for_all_merge) > 5:
          return list_for_all_merge[:5]


parser = imdb.IMDb()

def movie_data(list_movie_id, parser=parser):
    list_moviedata = []
    list_names = []
    list_urls = []
    list_imdb_movie_id = []

    for i in list_movie_id:
        list_imdb_movie_id.append(int(df_links.query(f'movieId=={i}').imdbId))

    for u, i in enumerate(list_imdb_movie_id):
        a = parser.get_movie(i)

        list_urls.append(a.get_fullsizeURL())
        a = a.data
        name = f'{u+1}) {a["localized title"]} ({a["year"]}) IMDb: {a["rating"]}'
        list_names.append(name)
    return (list_names, list_urls)
