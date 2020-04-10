from PlaylistSearcher import Song, WordQuery, db, User
from PlaylistSearcher.sources import update_lyrics_queue
from threading import Thread
import time
import regex
import queue


def strip_words(words):
    return words.split('&')[0].split(',')[0].lower()


def search_thread(query: WordQuery):
    user = User.query.filter(User.id == query.user).first()
    q = queue.Queue()
    list_of_songs = user.playlist_tracks(query.playlist)
    words = query.words.lower()
    threads = queue.Queue()
    # If we already checked just skip creating the thread
    for song in list_of_songs:
        if type(song) != Song:
            continue
        if song.lyrics:
            if len(words) < 8:
                re = regex.search(
                    rf'({words}){{e<=1}}', song.lyrics.lower())
            else:
                re = regex.search(
                    rf'({words}){{e<=3}}', song.lyrics.lower())
            if re is not None:
                query.result.append(song)
            query.searched += 1
            continue

        if song.last_check:
            if time.time() - song.last_check < 86400:
                query.searched += 1
                continue

        # We cannot move the original object because it is tied to this thread
        copysong = Song(
            song.name, song.artist, song.uri, song.image, song.preview
        )
        copysong.lyrics = song.lyrics
        copysong.source = song.source
        copysong.last_check = song.last_check
        threads.put([q, song, copysong])

    for counter in range(0, min(10, threads.qsize())):
        args = threads.get()
        thread = Thread(target=update_lyrics_queue, args=args)
        thread.start()

    for counter in range(query.total - query.searched):
        originalsong, song = q.get()
        if not threads.empty():
            args = threads.get()
            thread = Thread(target=update_lyrics_queue, args=args)
            thread.start()

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
