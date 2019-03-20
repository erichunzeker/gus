from manage import db,app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(8), nullable=False)
    type = db.Column(db.String(6), nullable=False)
    spotifyid = db.Column(db.String(22))
    lastfm = db.Column(db.String(100))
    deezer = db.Column(db.String(100))
    tidal = db.Column(db.String(100))
    soundcloud = db.Column(db.String(100))
    pandora = db.Column(db.String(100))
    play = db.Column(db.String(100))
    #Other identifiers that we might need