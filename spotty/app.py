"""Web application functions

Robert & Rodrico
2021/09/20"""


from .recomend import get_nn_query, query_nn_pickles, recomend
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import requests
import pickle
import os


def create_app():
    """Create App"""

    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def song_suggestor():
        """Create a suggestor route"""
        link = request.get_data('link')
        if link:
            try:
                # WHY MUST IT SCREW ME LIKE THIS
                link = str(link)[48:70]
                # ^^^ ACTUAL CRINGE ^^^

                links = recomend(link)

                message = 'Valid Link'
            except:
                message = 'Invalid Link'
        else:
            links = []
            message = ''

        return render_template('testsuggestor.html',
            links=links, message=message)


    return app