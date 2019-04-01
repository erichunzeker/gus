from flask import Flask, request, redirect, url_for, render_template, Response, jsonify, abort, session
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from time import sleep
from googleapiclient.discovery import build
import os, secrets, spotipy, pylast, pprint, deezer, tidalapi
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
deezer_secret = os.environ.get('DEEZER_SECRET')
deezer_id = os.environ.get('DEEZER_ID')
tidal_secret = os.environ.get('TIDAL_PASSWORD')
tidal_id = os.environ.get('TIDAL_LOGIN')
google_id = os.environ.get('GOOGLE_KEY')
soundcloud_id = os.environ.get('CX_SOUNDCLOUD')
pandora_id = os.environ.get('CX_PANDORA')
play_id = os.environ.get('CX_PLAY_MUSIC')

credentials = oauth2.SpotifyClientCredentials(
    client_id=spotify_id,
    client_secret=spotify_secret)

token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)

lastfm = pylast.LastFMNetwork(api_key=lastfm_id, api_secret=lastfm_secret)

deezerClient = deezer.Client()

tidal = tidalapi.Session()
tidal.login(tidal_id, tidal_secret)


pp = pprint.PrettyPrinter(indent=4)

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res

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
    print('here')
    song = db.session.query(Song).filter(Song.spotifyid == spotifyid and Song.type == type)
    print(song.count())
    if song.count() != 0:
        return redirect(url_for('load', url=song[0].url))

    key = generateKey()
    lstfm = "#"
    deez = "#"
    tide = "#"
    soundcloud = "#"
    pandora = "#"
    play = "#"
    if type == "album":
        result = spotify.album(spotifyid)
        album = result['name']
        artist = result['artists'][0]['name']
        lstfm = lastfm.get_album(artist, album).get_url()[26:]
        deezer = deezerClient.advanced_search({"artist": artist, "album": album}, relation="album")
        if len(deezer) != 0:
            deez = "album/" + str(deez[0].asdict()['id'])
        tid = tidal.search('album', album)
        for i in tid.albums:
            if i.name.lower().strip() == album.lower().strip() and i.artist.name.lower().strip() == artist.lower().strip():
                tide = "album/" + str(i.id)
                break
        result = google_search(album + " by " + artist, google_id, soundcloud_id)
        if 'item' in result.keys():
            for i in result['items']:
                if '/sets/' in i['link']:
                    soundcloud = i['link'][23:]
                    break
        result = google_search(album + " by " + artist, google_id, pandora_id)
        if 'item' in result.keys():
            for i in result['items']:
                pandora = i['link'][31:]
                break
        result = google_search(album + " by " + artist, google_id, play_id)
        if 'item' in result.keys():
            for i in result['items']:
                if 'https://play.google.com/store/music/' in i['link']:
                    print(i['link'])
                    play = i['link'][36:]
                    break
    elif type == "track":
        result = spotify.track(spotifyid)
        album = result['album']['name']
        track = result['name']
        artist = result['artists'][0]['name']
        lstfm = lastfm.get_track(artist, track).get_url()[26:]
        deezer = deezerClient.advanced_search({"artist": artist, "album": album, "track": track}, relation="track")
        if len(deezer) != 0:
            deez = "track/" + str(deezer[0].asdict()['id'])
        tid = tidal.search('track', track)
        for i in tid.tracks:
            if i.name.lower().strip() == track.lower().strip() and i.artist.name.lower().strip() == artist.lower().strip():
                tide = "track/" + str(i.id)
                break
        result = google_search(track + " by " + artist, google_id, soundcloud_id)
        if 'item' in result.keys():
            for i in result['items']:
                soundcloud = i['link'][23:]
                break
        result = google_search(track + " by " + artist, google_id, pandora_id)
        if 'item' in result.keys():
            for i in result['items']:
                pandora = i['link'][31:]
                break
        result = google_search(track + " by " + artist, google_id, play_id)
        if 'item' in result.keys():
            for i in result['items']:
                if 'https://play.google.com/store/music/' in i['link']:
                    print(i['link'])
                    play = i['link'][36:]
                    break
    elif type == "artist":
        result = spotify.artist(spotifyid)
        artist = result['name']
        lstfm = lastfm.get_artist(artist).get_url()[26:]
        deezer = deezerClient.advanced_search({"artist": artist}, relation="artist")
        if len(deezer) != 0:
            deez = "artist/" + str(deez[0].asdict()['id'])
        tid = tidal.search('artist', artist)
        if 'item' in result.keys():
            for i in tid.artists:
                if i.name.lower().strip() == artist.lower().strip():
                    tide = "artist/" + str(i.id)
                    break
        # Unable to do SoundCloud for artist
        result = google_search(artist, google_id, pandora_id)
        if 'item' in result.keys():
            for i in result['items']:
                pandora = i['link'][31:]
                break
        result = google_search(artist, google_id, play_id)
        if 'item' in result.keys():
            for i in result['items']:
                if 'https://play.google.com/store/music/' in i['link']:
                    print(i['link'])
                    play = i['link'][36:]
                    break
    song = Song(url=key, type=type, spotifyid=spotifyid, lastfm=lstfm, deezer=deez, tidal=tide, soundcloud=soundcloud, pandora=pandora, play=play)
    db.session.add(song)
    db.session.commit()
    return redirect(url_for('load', url=key))


@app.route('/s/<url>')
def load(url):
    song = db.session.query(Song).filter(Song.url == url)
    if song.count() == 0:
        return "404 url not in database"
    else:
        # v v v pass in links to this dictionary list v v v
        links = [{'spotify': ('https://open.spotify.com/' + song[0].type + '/' + song[0].spotifyid)}]
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

        return render_template('landing.html', link=links, data=data, url=url, info=info, song=song[0])


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