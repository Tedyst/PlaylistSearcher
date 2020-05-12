from flask import Flask
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
    uri = db.Column(db.String(20))
    image = db.Column(db.String(100))
    preview = db.Column(db.String(100))
    last_check = db.Column(db.Integer)

    def __init__(self, name, artist, uri, image, preview):
        self.name = name
        self.artist = artist
        self.uri = uri
        self.image = image
        self.preview = preview

    def __json__(self):
        data = {}
        data["name"] = self.name
        data["artist"] = self.artist
        data["lyrics"] = self.lyrics
        data["uri"] = self.uri
        data["image_url"] = self.image
        data["preview_url"] = self.preview
        if "lyrics_result" in vars(self):
            data["lyrics_result"] = self.lyrics_result
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

    def equal(self, user, words, playlist):
        if self.user == user:
            if self.words == words:
                if self.playlist == playlist:
                    return True
        return False


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

    def playlists(self):
        sp = spotipy.Spotify(self.token)
        playlists = sp.user_playlists(self.username)
        result = []
        for playlist in playlists['items']:
            result.append(Playlist(playlist['id'], playlist['name']))
        while playlists['next']:
            playlists = sp.next(playlists)
            for playlist in playlists['items']:
                result.append(Playlist(playlist['id'], playlist['name']))
        return result

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def _playlist_tracks(self, uri):
        sp = spotipy.Spotify(self.token)
        results = sp.user_playlist_tracks(
            self.username, playlist_id=uri, market="RO")
        tracks = []
        for track in results['items']:
            tracks.append(track['track'])
        while results['next']:
            results = sp.next(results)
            for track in results['items']:
                tracks.append(track['track'])
        return tracks

    def playlist_tracks(self, uri):
        result = []
        tracks = self._playlist_tracks(uri)
        for spotify_info in tracks:
            exists = Song.query.filter(Song.artist == spotify_info['artists'][0]['name']).filter(
                Song.name == spotify_info['name']).first()
            if not exists:
                exists = Song(
                    spotify_info['name'],
                    spotify_info['artists'][0]['name'],
                    spotify_info['uri'],
                    spotify_info['album']['images'][0]['url'],
                    spotify_info['preview_url']
                )
                db.session.add(exists)
            result.append(exists)
        db.session.commit()
        return result


class Playlist():
    def __init__(self, id, name):
        self.id = id
        self.name = name


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


db.create_all()
