import spotipy
import spotipy.util as util
from playlistutils import *
from config import *
import lyricsutils
import os 

try:
    os.mkdir('cache')
except:
    pass
    
scope = 'user-library-read'

username = 'vq0u2761le51p2idib6f89y78'
uri = 'spotify:playlist:6mw3LHMx8lUo0DbfQ3E4d8'
text = 'Only time will tell'

token = util.prompt_for_user_token(username, scope, client_id,
                                       client_secret, redirect_uri='https://stoicatedy.ovh')

if token:
    sp = spotipy.Spotify(auth=token)
    tracks = get_playlist_tracks(sp, username, uri)
    results = lyricsutils.find_songs(tracks, text)

else:
    print("Can't get token for", username)

