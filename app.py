from flask import Flask, request, redirect, url_for, render_template, Response, jsonify, abort
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from time import sleep
import os, secrets, spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from models import User, Song

spotify_secret = os.environ.get('SPOTIFY_SECRET')
spotify_id = os.environ.get('SPOTIFY_ID')

@app.route('/add/')
def webhook():
    key = secrets.token_urlsafe(6)
    while(db.session.query(Song).filter(Song.url == key).count() != 0):
       key = secrets.token_urlsafe(6)
    print("Key: " + key)
    credentials = SpotifyClientCredentials(spotify_id, spotify_secret)
    token = credentials.get_access_token()
    spotify = spotipy.Spotify(token)
    song = 'We Rise'
    artist = 'San Holo'
    results = spotify.search(q=song + ' artist:' + artist, type='track')
    print("SpotifyID: " + results['tracks']['items'][0]['id'])
    song = Song(url=key, spotifyid=results['tracks']['items'][0]['id'])
    db.session.add(song)
    db.session.commit()
    return "TEST"

@app.route('/s/<url>')
def load(url):
    song = db.session.query(Song).filter(Song.url == url)
    if(song.count() == 0):
        return "404 url not in database"
    else:
        return '<a href="https://open.spotify.com/track/'+ song[0].spotifyid+'">https://open.spotify.com/track/'+ song[0].spotifyid+'</a>'
    

if __name__ == '__main__':
    app.run()