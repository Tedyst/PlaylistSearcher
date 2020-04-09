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
    for song in tracks:
        exists = Song.query.filter(Song.artist == song['artists'][0]['name']).filter(
            Song.name == song['name']).first()
        if not exists:
            exists = Song(song['name'], song['artists'][0]['name'])
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
