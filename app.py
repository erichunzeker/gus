from flask import Flask, render_template, session
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



@app.route('/')
def homepage():
    name="one dance"
    results = spotify.search(q='track:' + name, type='track', limit=1)
    print(results)
    return render_template('home.html', data=results['tracks']['items'][0]['album']['images'][1]['url'])

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
