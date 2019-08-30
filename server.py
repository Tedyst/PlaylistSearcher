from bottle import route, run, get, response, request, redirect, template
import spotipy
from spotipy import oauth2
from config import *
import playlistutils
import lyricsutils

PORT_NUMBER = 8080
scope = 'user-library-read playlist-read-private'


@route('/')
def index():
    access_token = request.get_cookie("token")
    if access_token:
        sp = spotipy.Spotify(access_token)
        try:
            results = sp.current_user()
        except spotipy.client.SpotifyException:
            redirect("/authorization")
            return
        username = results['id']
        playlists = sp.user_playlists(username)
        # return playlists
        info = {'playlists': playlists['items']}
        return template('index.tpl', info)
    else:
        redirect("/authorization")


@route('/authorization')
def authorization():
    # Start new instance of spotipy
    sp_oauth = oauth2.SpotifyOAuth(
        client_id, client_secret, 'http://localhost:8080/authorization', scope=scope)
    access_token = ""

    # Get Token
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        response.set_header('Set-Cookie', 'token='+access_token)
        redirect("/")

    else:
        response.set_header(
            'Set-Cookie', 'token=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT')
        return htmlForLoginButton(sp_oauth)


@route('/search')
def search():
    # Get access token
    access_token = request.get_cookie("token")
    sp = None
    if access_token:
        sp = spotipy.Spotify(access_token)
        try:
            sp.current_user()
        except spotipy.client.SpotifyException:
            redirect("/authorization")
            return
    else:
        redirect("/authorization")
        return
    if sp is None:
        redirect("/authorization")
        return
    username = sp.current_user()['id']
    uri = request.query['playlist']
    text = request.query['text']
    print(text)
    tracks = playlistutils.get_playlist_tracks(sp, username, uri)
    results = lyricsutils.find_songs(tracks, text)
    info = {'results': results, 'text': text}
    return template('playlist.tpl', info)

def htmlForLoginButton(sp_oauth):
    auth_url = getSPOauthURI(sp_oauth)
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


def getSPOauthURI(sp_oauth):
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


run(host='', port=8080)
