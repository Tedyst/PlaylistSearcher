from PlaylistSearcher import APP, Song, WordQuery, db
from PlaylistSearcher.sources import update_lyrics
from fuzzywuzzy import fuzz


def strip_words(words):
    return words.split('&')[0].split(',')[0].lower()


def search_words(list_of_songs, words):
    result = []
    for song in list_of_songs:
        if type(song) != Song:
            continue
        update_lyrics(song)
        if song.lyrics:
            ratio = fuzz.partial_ratio(strip_words(song.lyrics),
                                       strip_words(words))
            if strip_words(words) in strip_words(song.lyrics):
                ratio = 100
            if ratio > 80:
                result.append(song)
    return song


def search_thread(query: WordQuery):
    list_of_songs = query.playlist
    words = query.words
    for song in list_of_songs:
        if type(song) != Song:
            continue
        update_lyrics(song)
        if song.lyrics:
            ratio = fuzz.partial_ratio(strip_words(song.lyrics),
                                       strip_words(words))
            if strip_words(words) in strip_words(song.lyrics):
                ratio = 100
            if ratio > 80:
                query.result.append(song)
    db.session.commit()
    return
