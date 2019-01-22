from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from models import User

spotify_secret = os.environ.get('SPOTIFY_SECRET')
spotify_id = os.environ.get('SPOTIFY_ID')

@app.route('/add/')
def webhook():
    name = "ram"
    email = "ram@ram.com"
    u = User(id = id, nickname = name, email = email)
    print("user created", u)
    db.session.add(u)
    db.session.commit()
    return "user created"

@app.route('/delete/')
def delete():
    u = User.query.get(i)
    db.session.delete(u)
    db.session.commit()
    return "user deleted"

if __name__ == '__main__':
    app.run()