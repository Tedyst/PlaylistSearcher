from PlaylistSearcher import APP, Song, db
from flask import Response
from PlaylistSearcher.sources import update_lyrics


@APP.route('/lyrics/<artist>/<name>')
def get_lyrics(artist, name):
    song = Song.query.filter(Song.artist == artist).filter(
        Song.name == name).first()
    if song is None:
        song = Song(name, artist)
        update_lyrics(song)

    db.session.commit()
    return Response(song.lyrics,
                    status=200)


if __name__ == "__main__":
    APP.run(threaded=True, debug=True)
