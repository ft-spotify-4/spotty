import pandas as pd
import pickle
import requests
import os

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import Normalizer

import plotly.express as px
from plotly.offline import plot

df = pd.read_csv('spotifyupload.csv', index_col=0)

CLIENT_ID = 'ffd61f80a4dd4d7c8fc0c289d994fec0'
CLIENT_SECRET = '4d2e3a2dc89c45be83eaa5083b9b1b48'

norm = pickle.load(open('norm.pkl', 'rb'))
knn = pickle.load(open('NN.pkl', 'rb'))

feature_columns = ['acousticness', 'danceability', 'duration_ms', 'energy',
       'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo',
       'valence']


def get_nn_query(track_id):
    """Get spotify request for song audio-features, format it for query_nn()."""
    # get access token
    AUTH_URL = 'https://accounts.spotify.com/api/token'
    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()
    # save the access token
    access_token = auth_response_data['access_token']

    # GET song audio-features
    headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}
    r = requests.get('https://api.spotify.com/v1/audio-features/' + track_id, headers=headers)
    song_dict = r.json()
    
    # put audio attributes in same order as in the dataframe the estimator is fit to.
    query_nn = [song_dict[x] for x in feature_columns]

    return query_nn


def query_nn_pickles(song_features):
    """Load pickles, scale song_features, return 5 nearest neighbors."""
    # scale features
    normed = norm.transform([song_features])
    # print(scaled)
    # get 5 nearest neighbors, returns a list of dataframe indices
    similar_five = knn.kneighbors(normed, 5, return_distance=False)

    return similar_five


def recomend(uri):
    """Take song_link, return 5 similar songs from dataframe."""
    # Slice uri out of spotify share link
    # uri = song_link[31:53]
    # Request song audio-features and format them for nearest-neighbors query
    features = get_nn_query(uri)
    # get nearest neighbors
    similar_songs = query_nn_pickles(features)

    # create links to spotify songs
    query_results = df.loc[similar_songs[0]]['url']
    art_tracks = df.loc[similar_songs[0]][['artist_name', 'track_name']].values
    links = query_results.tolist()
    # Wraps them together [artist, title, link]
    recommends = [[
        art_tracks[x][0], art_tracks[x][1],
        links[x]] for x in range(5)]
    return recommends, features


def make_graph(share_link, image_name, kind='png'):
    """Takes spotify share-link, export type, creates a png in an images folder, or a html div"""
    uri = share_link[31:53]
    # get song features
    song_features = get_nn_query(uri)
    # scale to [0,1]
    normed = norm.transform([song_features])
    # put in a df as expected by plotly
    dfq = pd.DataFrame(dict(r=normed[0], theta=feature_columns))
    # a polar plot
    fig = px.line_polar(dfq, r='r', theta='theta', line_close=True)
    # look nice plot
    fig.update_polars(radialaxis_showticklabels=False, radialaxis_showgrid=False)
    fig.update_traces(fill='toself')
    # if kwarg is 'div' return a div which can be put in an html doc
    if kind == 'div':
        plt_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plt_div
    # default kwarg 'png' save png to an images folder, create one if none exist
    if kind == 'png':
        if not os.path.exists("images"):
            os.mkdir("images")
        
        fig.write_image(f"images/{image_name}.png", width=300, height=300)
        return None
