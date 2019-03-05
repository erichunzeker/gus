from manage import db,app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(8), nullable=False)
    spotifyid = db.Column(db.String(22))
    #Other identifiers that we might need