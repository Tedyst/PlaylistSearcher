from PlaylistSearcher import APP, Song, WordQuery, db, User
from PlaylistSearcher.sources import update_lyrics
from fuzzywuzzy import fuzz
from PlaylistSearcher.playlist import playlist_tracks
from threading import Thread
import time


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
    threads = []
    words = query.words
    for song in list_of_songs:
        if type(song) != Song:
            continue
        if song.last_check:
            if time.time() - song.last_check < 86400:
                # Check now, do not create another thread
                if song.lyrics:
                    ratio = fuzz.partial_ratio(strip_words(song.lyrics),
                                               strip_words(words))
                    if strip_words(words) in strip_words(song.lyrics):
                        ratio = 100
                    if ratio > 80:
                        query.result.append(song)
                else:
                    query.notfound.append(song)
                query.searched += 1
                continue

        copysong = Song(song.name, song.artist)
        copysong.lyrics = song.lyrics
        copysong.source = song.source
        copysong.last_check = song.last_check
        thread = Thread(target=update_lyrics,
                        args=[copysong])
        thread.start()
        threads.append([thread, copysong, song])

    for couple in threads:
        thread = couple[0]
        song = couple[1]
        originalsong = couple[2]
        originalsong.lyrics = song.lyrics
        originalsong.source = song.source
        originalsong.last_check = song.last_check
        thread.join()
        if song.lyrics:
            ratio = fuzz.partial_ratio(strip_words(song.lyrics),
                                       strip_words(words))
            if strip_words(words) in strip_words(song.lyrics):
                ratio = 100
            if ratio > 80:
                query.result.append(song)
        else:
            query.notfound.append(song)
        query.searched += 1
    db.session.commit()
    return
