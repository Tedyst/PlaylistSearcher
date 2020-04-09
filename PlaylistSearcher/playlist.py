from PlaylistSearcher import Song, User, db, Playlist
import spotipy


def _playlist_tracks(user: User, uri):
    sp = spotipy.Spotify(user.token)
    results = sp.user_playlist_tracks(user.username, playlist_id=uri)
    tracks = []
    for track in results['items']:
        tracks.append(track['track'])
    while results['next']:
        results = sp.next(results)
        for track in results['items']:
            tracks.append(track['track'])
    return tracks


def playlist_tracks(user: User, uri):
    result = []
    tracks = _playlist_tracks(user, uri)
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


def user_playists(user: User):
    sp = spotipy.Spotify(user.token)
    playlists = sp.user_playlists(user.username)
    result = []
    for playlist in playlists['items']:
        result.append(Playlist(playlist['id'], playlist['name']))
    while playlists['next']:
        playlists = sp.next(playlists)
        for playlist in playlists['items']:
            result.append(Playlist(playlist['id'], playlist['name']))
    return result
