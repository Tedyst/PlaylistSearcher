import lyricsgenius
import os 
import youtube_dl
from fuzzywuzzy import fuzz

# Init things
ydl_opts = {
    'quiet': True,
    'skip_download': True,
}
ydl = youtube_dl.YoutubeDL(ydl_opts)

genius = lyricsgenius.Genius(
    "m0M1r-FPGb7n-Y5NeVu1jqtcd7MAcmnTLzsxRQADXHo_PE9WapuywBSGwKtBfG3Z")
genius.verbose = False
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]

def stripartist(artist):
    return artist.split('&')[0].split(',')[0].replace(' ', '').lower()

def get_lyrics_Genius(name, artist):
    song = genius.search_song(name, artist.split('&')[
                              0].replace(' ', '').lower())

    if song is None:
        return None
    
    # Making every change possible to make the strings match, while still being reasonable
    if fuzz.ratio(stripartist(artist), stripartist(song.artist)) > 80:
        return song.lyrics

    print("Not found Genius lyrics for", name, artist)
    print("Found only", song.title, song.artist.split('&')[0].replace(' ', ''),
          ", which has", fuzz.ratio(artist.split('&')[0].replace(' ', ''), song.artist.split('&')[0].replace(' ', '')), "% accuracy")
    return None

def get_lyrics_youtube(name, artist):
    lyrics = ""
    try:
        info = ydl.extract_info("ytsearch:" + name + '-' + artist)['entries'][0]['description']
    except:
        return None
    if "Lyrics:" in info:
        lyrics = info.split('Lyrics:')[1]
    elif "Lyrics" in info:
        lyrics = info.split('Lyrics')[1]
    elif "L Y R I C S:" in info:
        lyrics = info.split('L Y R I C S:')[1]
    elif "L Y R I C S" in info:
        lyrics = info.split('L Y R I C S')[1]
    else:
        return None
    print("Downloaded lyrics from youtube description for", name, artist)
    return lyrics

def is_not_found(name, artist):
    file = open('notfoundsongs.txt', 'r')
    data = file.read()
    file.close()
    if name+' - '+artist in data:
        return True
    return False

def add_not_found(name, artist):
    file = open('notfoundsongs.txt', 'a+')
    file.write(name+' - '+artist+'\n')
    file.close()
    

def cache(name, artist):
    if (os.path.isfile('cache/' + artist + ' - ' + name)):
        file = open('cache/' + artist + ' - ' + name, 'r')
        data = file.read()
        file.close()
        return data
    return None

def get_lyrics(name, artist):
    # Already found, serve it
    lyrics_cache = cache(name, artist)
    if lyrics_cache != None:
        return lyrics_cache

    # Already searched, skip
    if is_not_found(name, artist):
        return None
    
    # Search on genius
    lyrics_genius = get_lyrics_Genius(name, artist)
    if lyrics_genius != None:
        file = open('cache/' + artist + ' - ' + name, 'w')
        file.write(lyrics_genius)
        file.close()
        return lyrics_genius
    
    # Search on youtube
    lyrics_youtube = get_lyrics_youtube(name, artist)
    if lyrics_youtube != None:
        file = open('cache/' + artist + ' - ' + name, 'w')
        file.write(lyrics_youtube)
        file.close()
        return lyrics_youtube

    add_not_found(name, artist)
    return None

def search_lyrics(name, artist, lyrics, text):
    a = fuzz.partial_ratio(text, lyrics)
    if a > 80:
        return True
    return False

def find_songs(tracks, text):
    results = []
    for i in tracks:
        lyric = lyricsutils.get_lyrics(i.name, i.main_artist)
        if lyric is not None:
            if lyricsutils.search_lyrics(i.name, i.main_artist, lyric, text):
                print("Found match for", text, "in song", i.name, i.main_artist)
                results.append(i)

    return results
