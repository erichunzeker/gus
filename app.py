from flask import Flask, render_template, session, request
from flask_sqlalchemy import SQLAlchemy
import os
import json, requests
import spotipy
import spotipy.oauth2 as oauth2


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from models import User

spotify_secret = os.environ.get('SPOTIFY_SECRET')
spotify_id = os.environ.get('SPOTIFY_ID')


credentials = oauth2.SpotifyClientCredentials(
        client_id=spotify_id,
        client_secret=spotify_secret)

token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)



@app.route('/', methods=['GET', 'POST'])
def homepage():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        results = spotify.search(q='track:' + name, type='track', limit=10)
        count = 0
        data = []

        for i in results['tracks']['items']:
            data.append({"img": results['tracks']['items'][count]['album']['images'][0]['url'],
                        "name": results['tracks']['items'][count]['name'],
                        "artist": results['tracks']['items'][count]['album']['artists'][0]['name']})
            count += 1

        print(data)
        # make dict with limit of ten: img, name, artist
        # [ {img, name, artist}, {img, name, artist} ]
        return render_template('home.html', data=data)
    return render_template('home.html', error=error)


@app.route('/add/')
def webhook():
    name = "ram"
    email = "ram@ram.com"
    u = User(nickname=name, email=email)
    print("user created", u)
    db.session.add(u)
    db.session.commit()
    return "user created"


@app.route('/delete/')
def delete():
    u = User.query.get()
    db.session.delete(u)
    db.session.commit()
    return "user deleted"


if __name__ == '__main__':
    app.run()
