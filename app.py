from PlaylistSearcher import APP, Song, db, User, login_manager, WordQuery
from flask import Response, url_for, request, redirect, render_template
from PlaylistSearcher.sources import update_lyrics
from flask_login import current_user, login_user, login_required
import spotipy
import PlaylistSearcher.config as config
import PlaylistSearcher.playlist as playlist
from threading import Thread
import PlaylistSearcher.lyricsutils as lyricsutils
import json


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


@APP.route('/authorization')
def authorization():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        config.SPOTIFY_CLIENT_ID,
        config.SPOTIFY_CLIENT_SECRET,
        url_for('authorization', _external=True),
        scope="user-library-read playlist-read-private playlist-read-collaborative")
    if current_user.is_authenticated:
        if current_user.valid():
            return Response(current_user.token,
                            status=200)

    url = request.url
    code = sp_oauth.parse_response_code(url)
    if code:
        APP.logger.info(
            "Found Spotify auth code in Request URL!")
        APP.logger.debug("Spotify auth code is %s", code)
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        token = token_info['access_token']
        me = spotipy.Spotify(token).me()
        username = me['id']

        user = User.query.filter(User.username == username).first()
        if user is None:
            user = User(username, token)
            db.session.add(user)
            db.session.commit()

        user.token = token
        login_user(user, remember=True)
        return Response(user.token,
                        status=200)
    else:
        url = sp_oauth.get_authorize_url()
        return Response(url,
                        status=200)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('authorization'))


@APP.route('/playlists')
@login_required
def playlists():
    string = ""
    playlists = playlist.user_playists(current_user)
    for i in playlists:
        string += i.name + ' - ' + i.id + '<br>'
    return Response(string,
                    status=200)


@APP.route('/search')
@login_required
def search():
    return render_template('search.html')


@APP.route('/ajax/<playlist_id>/<words>')
@login_required
def ajax(playlist_id, words):
    if current_user.current_query is None:
        current_user.current_query = WordQuery(playlist_id, words)
        thread = Thread(target=lyricsutils.search_thread,
                        args=[current_user.current_query])
        thread.start()
    else:
        if current_user.current_query.words != words or current_user.current_query.playlist_id != playlist_id:
            current_user.current_query = WordQuery(playlist_id, words)
            thread = Thread(target=lyricsutils.search_thread,
                            args=[current_user.current_query])
            thread.start()
    return Response(json.dumps([i.__json__() for i in current_user.current_query.result]),
                    status=200)


if __name__ == "__main__":
    APP.run(threaded=True, debug=True)
