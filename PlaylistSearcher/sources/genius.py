import lyricsgenius
from PlaylistSearcher import APP, Song
from fuzzywuzzy import fuzz
from PlaylistSearcher.config import GENIUS_TOKEN

SOURCE_NAME = "Genius"
genius = lyricsgenius.Genius(GENIUS_TOKEN)

if APP.debug:
    genius.verbose = True
else:
    genius.verbose = False
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]


def strip_artist(artist):
    return artist.split('&')[0].split(',')[0].replace(' ', '').lower()


def get_lyrics(song: Song):
    result = genius.search_song(song.name, song.artist.split('&')[
        0].replace(' ', '').lower())

    if song is None:
        return None

    # Making every change possible to make the strings match
    ratio = fuzz.ratio(strip_artist(song.artist),
                       strip_artist(result.artist))
    if ratio > 80:
        APP.logger.debug(
            "Found Genius lyric with %s accuracy for %s, found %s",
            ratio, song.name + song.artist, result.title)
        return result.lyrics

    APP.logger.debug(
        "Skipped Genius lyric with %s accuracy for %s, found %s",
        ratio, song.title, result.title)
    APP.logger.debug(
        "Artist fuzzyness was %s    %s",
        song.artist, result.artist)
    return None
