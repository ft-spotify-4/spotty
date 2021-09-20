"""Web application functions

Robert & Rodrico
2021/09/20"""


from flask import Flask, render_template, request
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import requests
import pickle
import os


load_dotenv()
neigh = pickle.load(open('spotty_model', 'rb'))


AUTH_URL = 'https://accounts.spotify.com/api/token'
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': os.getenv('CLIENT_ID'),
    'client_secret': os.getenv('CLIENT_SECRET')
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {
    'Authorization': f'Bearer {access_token}'
}
BASE_URL = 'https://api.spotify.com/v1/'


songs_df = pd.read_csv('genres_v2.csv')
df = pd.read_csv('updated.csv')


scaler = StandardScaler()
scaler.fit(df)


def create_app():
    """Create App"""

    app = Flask(__name__)

    
    @app.route('/')
    def base():
        """Creates the home page"""

        return render_template('testindex.html')

    @app.route('/song_suggestor', methods=['GET', 'POST'])
    def song_suggestor():
        """Create a suggestor route"""
        track = request.get_data('track')

        if track:
            r = requests.get(BASE_URL + 'audio-features/' + str(track),
                headers=headers)
            song_dict = r.json()

            query_nn = np.array([song_dict[x] for x in df.columns])

            api_similars = neigh.kneighbors(scaler.tranform([query_nn]),
                5, return_distance=False)
            query_results = songs_df.loc[api_similars[0]]['uri']

            links = query_results.apply(
                lambda x: 'https://open.spotify.com/track/' + x[14:]
            )
        else:
            linky = "Similar songs will go here"

        return render_template('testsuggestor.html', linky=linky)


    return app