class Song:
    def __init__(self, name, main_artist):
        self.name = name.split('(')[0]
        self.main_artist = main_artist



def get_playlist_tracks(client, username, uri):
    results = client.user_playlist_tracks(username, playlist_id=uri)
    tracks = []
    for i in results['items']:
        song = Song(i['track']['name'], i['track']['artists'][0]['name'])
        if "Various " in song.main_artist:
            song.main_artist = i['track']['artists'][1]['name']
        tracks.append(song)
    while results['next']:
        results = client.next(results)
        for i in results['items']:
            song = Song(i['track']['name'], i['track']['artists'][0]['name'])
            if "Various " in song.main_artist:
                song.main_artist = i['track']['artists'][1]['name']
            tracks.append(song)
    return tracks
