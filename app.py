from flask import Flask, request, redirect, url_for, render_template, Response, jsonify, abort, session
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from time import sleep
import os, secrets, spotipy, pylast, pprint
import spotipy.oauth2 as oauth2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from models import User, Song

spotify_secret = os.environ.get('SPOTIFY_SECRET')
spotify_id = os.environ.get('SPOTIFY_ID')
lastfm_secret = os.environ.get('LASTFM_SECRET')
lastfm_id = os.environ.get('LASTFM_KEY')


credentials = oauth2.SpotifyClientCredentials(
        client_id=spotify_id,
        client_secret=spotify_secret)

token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)

lastfm = pylast.LastFMNetwork(api_key=lastfm_id, api_secret=lastfm_secret)

pp = pprint.PrettyPrinter(indent=4)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        toggle = request.form['toggle']
        results = spotify.search(q=toggle + ':' + name, type=toggle, limit=10)
        count = 0
        data = []
        #print(results)

        if toggle == 'track':
            for i in results['tracks']['items']:
                if len(results['tracks']['items'][count]['album']['images']) == 0:
                    data.append({"img": "static/img/note.png",
                                 "name": results['tracks']['items'][count]['name'],
                                 "artist": results['tracks']['items'][count]['album']['artists'][0]['name'],
                                 "spotifyid": results['tracks']['items'][count]['id']})
                else:
                    data.append({"img": results['tracks']['items'][count]['album']['images'][0]['url'],
                                "name": results['tracks']['items'][count]['name'],
                                "artist": results['tracks']['items'][count]['album']['artists'][0]['name'],
                                "spotifyid": results['tracks']['items'][count]['id']})
                count += 1

        elif toggle == 'artist':
            for i in results['artists']['items']:
                if len(results['artists']['items'][count]['images']) == 0:
                    data.append({"img": "static/img/note.png",
                                 "name": results['artists']['items'][count]['name'],
                                 "artist": results['artists']['items'][count]['name'],
                                 "spotifyid": results['artists']['items'][count]['id']})
                else:
                    data.append({"img": results['artists']['items'][count]['images'][0]['url'],
                                "name": results['artists']['items'][count]['name'],
                                "artist": results['artists']['items'][count]['name'],
                                "spotifyid": results['artists']['items'][count]['id']})
                count += 1
        else:
            for i in results['albums']['items']:
                if len(results['albums']['items'][count]['images']) == 0:
                    data.append({"img": "static/img/note.png",
                                 "name": results['albums']['items'][count]['name'],
                                 "artist": results['albums']['items'][count]['artists'][0]['name'],
                                 "spotifyid": results['albums']['items'][count]['id']})
                else:
                    data.append({"img": results['albums']['items'][count]['images'][0]['url'],
                                "name": results['albums']['items'][count]['name'],
                                "artist": results['albums']['items'][count]['artists'][0]['name'],
                                "spotifyid": results['albums']['items'][count]['id']})
                count += 1
        #print(data)
        # make dict with limit of ten: img, name, artist
        # [ {img, name, artist}, {img, name, artist} ]
        return render_template('home.html', data=data, type=toggle)
    return render_template('home.html', error=error)

def generateKey():
    key = secrets.token_urlsafe(6)
    while(db.session.query(Song).filter(Song.url == key).count() != 0):
       key = secrets.token_urlsafe(6)
    return key

@app.route('/create/<type>/<spotifyid>')
def create(type, spotifyid):
    key = generateKey()
    lstfm = ""
    if type == "album":
        result = spotify.album(spotifyid)
        album = result['name']
        artist = result['artists'][0]['name']
        lstfm = lastfm.get_album(artist, album).get_url()[26:]
    elif type == "track":
        result = spotify.track(spotifyid)
        album = result['album']['name']
        track = result['name']
        artist = result['artists'][0]['name']
        lstfm = lastfm.get_track(artist, track).get_url()[26:]
    elif type == "artist":
        result = spotify.artist(spotifyid)
        artist = result['name']
        lstfm = lastfm.get_artist(artist).get_url()[26:]
    song = Song(url=key, type=type, spotifyid=spotifyid, lastfm=lstfm)
    db.session.add(song)
    db.session.commit()
    return redirect(url_for('load', url=key))

@app.route('/s/<url>')
def load(url):
    song = db.session.query(Song).filter(Song.url == url)
    if(song.count() == 0):
        return "404 url not in database"
    else:
        return '<a href="https://open.spotify.com/' + song[0].type + '/'+ song[0].spotifyid+'">https://open.spotify.com/' + song[0].type + '/'+ song[0].spotifyid + '</a><br><a href="https://www.last.fm/music/' + song[0].lastfm + '">https://www.last.fm/music/' + song[0].lastfm + '</a>'

if __name__ == '__main__':
    app.run()
