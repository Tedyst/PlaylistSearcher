from PlaylistSearcher import Song, WordQuery, db, User
from PlaylistSearcher.sources import update_lyrics_queue
from PlaylistSearcher.playlist import playlist_tracks
from threading import Thread
import time
import regex
import queue


def strip_words(words):
    return words.split('&')[0].split(',')[0].lower()


def search_words(list_of_songs, words):
    result = []
    for song in list_of_songs:
        if type(song) != Song:
            continue
        update_lyrics(song)
        if song.lyrics:
            if len(words) < 8:
                re = regex.search(
                    rf'({words}){{e<=1}}', song.lyrics.lower())
            else:
                re = regex.search(
                    rf'({words}){{e<=3}}', song.lyrics.lower())
            if re is not None:
                result.append(song)
    return song


def search_thread(query: WordQuery):
    user = User.query.filter(User.id == query.user).first()
    q = queue.Queue()
    list_of_songs = playlist_tracks(user, query.playlist)
    threads = []
    words = query.words.lower()
    for song in list_of_songs:
        if type(song) != Song:
            continue
        if song.last_check:
            if time.time() - song.last_check < 86400:
                # Check now, do not create another thread
                if song.lyrics:
                    if len(words) < 8:
                        re = regex.search(
                            rf'({words}){{e<=1}}', song.lyrics.lower())
                    else:
                        re = regex.search(
                            rf'({words}){{e<=3}}', song.lyrics.lower())
                    if re is not None:
                        query.result.append(song)
                else:
                    query.notfound.append(song)
                query.searched += 1
                continue

        copysong = Song(
            song.name, song.artist, song.uri, song.image, song.preview
        )
        copysong.lyrics = song.lyrics
        copysong.source = song.source
        copysong.last_check = song.last_check

        thread = Thread(target=update_lyrics_queue,
                        args=[q, song, copysong])
        thread.start()

    for counter in range(len(list_of_songs)):
        originalsong, song = q.get()

        originalsong.lyrics = song.lyrics
        originalsong.source = song.source
        originalsong.last_check = song.last_check
        if song.lyrics:
            re = regex.search(
                rf'({words}){{e<=3}}', song.lyrics.lower())
            if re is not None:
                query.result.append(song)
        else:
            query.notfound.append(song)
        query.searched += 1
    db.session.commit()
    return
