from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from logging import DEBUG, INFO
import sys
import PlaylistSearcher.config as config
from flask_login import LoginManager
import spotipy

APP = Flask(__name__,
            template_folder='../templates',
            static_folder="../static")
APP.config['SECRET_KEY'] = config.SECRET_KEY
APP.config['SQLALCHEMY_ECHO'] = False
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.logger.setLevel(INFO)

# Debug mode
if APP.debug:
    APP.config['DEBUG_TB_PROFILER_ENABLED'] = True
    toolbar = DebugToolbarExtension(APP)
    APP.logger.setLevel(DEBUG)

if "pytest" in sys.modules:
    APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data.db'

db = SQLAlchemy(APP, session_options={
    'expire_on_commit': False
})
login_manager = LoginManager(APP)


class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    artist = db.Column(db.String(50))
    lyrics = db.Column(db.String(5000))
    source = db.Column(db.String(10))
    last_check = db.Column(db.Integer)

    def __init__(self, name, artist):
        self.name = name
        self.artist = artist

    def __json__(self):
        data = {}
        data["name"] = self.name
        data["artist"] = self.artist
        data["lyrics"] = self.lyrics
        return data

    @property
    def title(self):
        return self.name + ' - ' + self.artist


query_queue = []


class WordQuery():
    def __init__(self, user, playlist, words, total):
        self.user = user
        self.playlist = playlist
        self.words = words
        self.result = []
        self.searched = 0
        self.notfound = []
        self.total = total


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    displayname = db.Column(db.String(50))
    token = db.Column(db.String(100))

    def __init__(self, username, token):
        self.username = username
        self.token = token

    def valid(self):
        if self.token is None:
            return False
        sp = spotipy.Spotify(self.token)
        try:
            me = sp.me()
        except spotipy.client.SpotifyException:
            return False
        if me is None:
            return False
        if me['id'] != self.username:
            return False
        return True

    @property
    def name(self):
        if self.displayname:
            return self.displayname
        return self.username

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return self.id


class Playlist():
    def __init__(self, id, name):
        self.id = id
        self.name = name


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


db.create_all()
