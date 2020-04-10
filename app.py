from PlaylistSearcher import APP, Song, db, User, login_manager, WordQuery, query_queue
from flask import Response, url_for, request, redirect, render_template
from PlaylistSearcher.sources import update_lyrics
from flask_login import current_user, login_user, login_required
import spotipy
import PlaylistSearcher.config as config
from threading import Thread
import PlaylistSearcher.lyricsutils as lyricsutils
import json


@APP.route('/lyrics/<uri>')
def get_lyrics(uri):
    song_info = spotipy.Spotify().track(uri)
    song = Song.query.filter(Song.artist == song_info['artists'][0]['name']
                             ).filter(Song.name == song_info['name']).first()
    if song is None:
        song = Song(
            song_info['name'],
            song_info['artists'][0]['name'],
            song_info['uri'],
            song_info['album']['images'][0]['url'],
            song_info['preview_url']
        )
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
            redirect(url_for('search'))

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

        user.token = token
        db.session.add(user)
        db.session.commit()
        login_user(user)
        pint = []
        for playlistasd in user.playlists():
            pint.append(playlistasd.id)
        APP.logger.info("Playlists for %s: %s",
                        user.username, json.dumps(pint))
        return redirect(url_for('search'))
    else:
        url = sp_oauth.get_authorize_url()
        return render_template('login.html', auth_url=url)


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


@APP.route('/')
@login_required
def search():
    if not current_user.valid():
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            config.SPOTIFY_CLIENT_ID,
            config.SPOTIFY_CLIENT_SECRET,
            url_for('authorization', _external=True),
            scope="user-library-read playlist-read-private playlist-read-collaborative")
        url = sp_oauth.get_authorize_url()
        return render_template('login.html', auth_url=url)
    return render_template('search.html')


@APP.route('/ajax/<playlist_id>/<words>')
@login_required
def ajax(playlist_id, words):
    query = None
    for i in query_queue:
        if i.user == current_user.id and i.words == words and i.playlist == playlist_id:
            query = i
            break
    if query is None:
        startthread = True
        for i in query_queue:
            if i.playlist == playlist_id:
                startthread = False
                break
        if startthread:
            query = WordQuery(current_user.id, playlist_id, words,
                              len(current_user.playlist_tracks(playlist_id)))
            query_queue.append(query)
            thread = Thread(target=lyricsutils.search_thread,
                            args=[query])
            thread.start()
    result = {
        "finished": True,
        "total": query.total,
        "searched": query.searched,
        "notfound": [i.__json__() for i in query.notfound],
        "results": [i.__json__() for i in query.result]
    }
    if query.searched != query.total:
        result["finished"] = False
    return Response(json.dumps(result),
                    status=200,
                    mimetype='application/json')


if __name__ == "__main__":
    APP.run(threaded=True, debug=True)
