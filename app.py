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
from services import get_services, google_search, Deezer, Tidal, Soundcloud, Pandora, Play

#gather and setup spotify credentials
spotify_secret = os.environ.get('SPOTIFY_SECRET')
spotify_id = os.environ.get('SPOTIFY_ID')

credentials = oauth2.SpotifyClientCredentials(
    client_id=spotify_id,
    client_secret=spotify_secret)

token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)

pp = pprint.PrettyPrinter(indent=4)

@app.route('/', methods=['GET', 'POST'])
def homepage():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        toggle = request.form['toggle']
        data = getdata(toggle, name)
        return render_template('home.html', data=data, type=toggle)
    return render_template('home.html', error=error)


def generateKey():
    key = secrets.token_urlsafe(6)
    while db.session.query(Song).filter(Song.url == key).count() != 0:
        key = secrets.token_urlsafe(6)
    return key


@app.route('/create/<type>/<spotifyid>')
def create(type, spotifyid):
    song = db.session.query(Song).filter(Song.spotifyid == spotifyid and Song.type == type)
    if song.count() != 0:
        return redirect(url_for('load', url=song[0].url))
    
    key = generateKey()
    info = get_music_info(type, spotifyid)
    services = get_services(type, info[0], info[1], info[2])
    
    song = Song(url=key, type=type, spotifyid=spotifyid, lastfm=services['lstfm'], deezer=services['deez'], tidal=services['tide'],     soundcloud=services['soundcloud'], pandora=services['pandora'], play=services['play'])
    
    db.session.add(song)
    db.session.commit()
    return redirect(url_for('load', url=key))


def get_music_info(type, spotifyid):
    album = ""
    track = ""
    artist = ""
    if type == "album":
        result = spotify.album(spotifyid)
        album = result['name']
        artist = result['artists'][0]['name']
    elif type == "track":
        result = spotify.track(spotifyid)
        album = result['album']['name']
        track = result['name']
        artist = result['artists'][0]['name']
    elif type == "artist":
        result = spotify.artist(spotifyid)
        artist = result['name']
    return [album, track, artist]
    
    
@app.route('/s/<url>')
def load(url):
    song = db.session.query(Song).filter(Song.url == url)
    if song.count() == 0:
        return "404 url not in database"
    else:
        # v v v pass in links to this dictionary list v v v
        links = {'spotify': ('https://open.spotify.com/' + song[0].type + '/' + song[0].spotifyid)}
        print('https://open.spotify.com/' + song[0].type + '/' + song[0].spotifyid)
        #TODO get the rest of the links from song and add them to links list
        data = fetchattributes(song[0].type, song[0].spotifyid)
        if song[0].type == 'track':
            if len(data['album']['images']) != 0:
                info = {'name': data['name'], 'artist': data['artists'][0]['name'], 'img': data['album']['images'][0]['url']}
            else:
                info = {'name': data['name'], 'artist': data['artists'][0]['name'], 'img': "http://g-u-s.herokuapp.com/static/img/note.png"}
        elif song[0].type == 'album':
            if len(data['images']) != 0:
                info = {'name': data['name'], 'artist': data['artists'][0]['name'], 'img': data['images'][0]['url']}
            else:
                info = {'name': data['name'], 'artist': data['artists'][0]['name'], 'img': "http://g-u-s.herokuapp.com/static/img/note.png"}
        else:
            if len(data['images']) != 0:
                info = {'name': data['name'], 'artist': data['name'], 'img': data['images'][0]['url']}
            else:
                info = {'name': data['name'], 'artist': data['name'], 'img': "http://g-u-s.herokuapp.com/static/img/note.png"}

        return render_template('landing.html', link=links, data=data, url=url, info=info )


def fetchattributes(type, id):
    if type == 'track':
        return spotify.track(id)
    elif type == 'album':
        return spotify.album(id)
    else:
        return spotify.artist(id)


def getdata(toggle, query):
    count = 0
    data = []
    results = spotify.search(q=toggle + ':' + query, type=toggle, limit=15)

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

    return data

if __name__ == '__main__':
    app.run()
