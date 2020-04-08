from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from logging import DEBUG, INFO
import sys
import PlaylistSearcher.config as config

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

db = SQLAlchemy(APP)


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

    @property
    def title(self):
        return self.name + ' - ' + self.artist


db.create_all()
