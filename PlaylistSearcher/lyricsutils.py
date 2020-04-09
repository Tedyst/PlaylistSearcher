from PlaylistSearcher import APP, Song, WordQuery, db, User
from PlaylistSearcher.sources import update_lyrics
from fuzzywuzzy import fuzz
from PlaylistSearcher.playlist import playlist_tracks


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
    user = User.query.filter(User.id == query.user).first()
    list_of_songs = playlist_tracks(user, query.playlist)
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
        else:
            query.notfound += 1
        query.searched += 1
    db.session.commit()
    return
