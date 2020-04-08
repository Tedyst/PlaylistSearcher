import lyricsgenius
import os 
import youtube_dl
from fuzzywuzzy import fuzz
from multiprocessing.dummy import Pool as ThreadPool
from diskcache import Cache

cache = Cache("cache")


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


def get_lyrics(name, artist):
    print(name, artist)
    # Already found, serve it
    lyrics_cache = cache.get([name, artist])
    if lyrics_cache is not None:
        if lyrics_cache[1] is False:
            return None
        return lyrics_cache[0]

    # Search on genius
    lyrics_genius = get_lyrics_Genius(name, artist)
    if lyrics_genius is not None:
        cache.add([name, artist], [lyrics_genius, True])
        return lyrics_genius

    # Search on youtube
    lyrics_youtube = get_lyrics_youtube(name, artist)
    if lyrics_youtube is not None:
        cache.add([name, artist], [lyrics_youtube, True])
        return lyrics_youtube

    cache.add([name, artist], [None, False])
    return None


def search_lyrics(track, text):
    name = track.name
    artist = track.main_artist
    lyrics = get_lyrics(name, artist)
    if lyrics is None:
        return None
    a = 0
    if text.lower() in lyrics.lower():
        a = 100
    # else:
    #     a = fuzz.partial_ratio(text, lyrics)
    if a > 80:
        return track
    return None


def find_songs(tracks, text):
    results = []
    pool = ThreadPool(10)

    for i in tracks:
        results.append(pool.apply_async(search_lyrics, args=(i, text)))

    pool.close()
    pool.join()
    result = []
    for i in range(len(results)):
        if results[i].get() is not None:
            result.append(results[i].get())
    return result


def get_not_found():
    for i in cache:
        if cache[i][1] is False:
            print(i)
