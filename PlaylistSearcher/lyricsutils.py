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

        # We cannot move the original object because it is tied to this thread
        copysong = Song(
            song.name, song.artist, song.uri, song.image, song.preview
        )
        copysong.lyrics = song.lyrics
        copysong.source = song.source
        copysong.last_check = song.last_check
        if copysong.lyrics:
            if len(words) < 8:
                re = regex.search(
                    rf'({words}){{e<=1}}', copysong.lyrics.lower())
            else:
                re = regex.search(
                    rf'({words}){{e<=2}}', copysong.lyrics.lower())
            if re is not None:
                start, end = re.span()
                if copysong.lyrics[start:start+2] == "r>":
                    start += 2
                elif copysong.lyrics[start] == ">":
                    start += 1
                copysong.lyrics = copysong.lyrics[:start] + "<mark>" + \
                    copysong.lyrics[start:end] + \
                    "</mark>" + copysong.lyrics[end:]
                query.result.append(copysong)
            query.searched += 1
            continue

        if copysong.last_check:
            if time.time() - copysong.last_check < 86400:
                query.searched += 1
                continue

        threads.put([q, song, copysong])

    # Starting the threads
    for counter in range(0, min(10, threads.qsize())):
        args = threads.get()
        thread = Thread(target=update_lyrics_queue, args=args)
        thread.start()

    # Getting the result from the threads
    for counter in range(query.total - query.searched):
        song, copysong = q.get()
        if not threads.empty():
            args = threads.get()
            thread = Thread(target=update_lyrics_queue, args=args)
            thread.start()

        # Update song (the one tied to the database)
        song.lyrics = song.lyrics
        song.source = song.source
        song.last_check = song.last_check

        if copysong.lyrics:
            if len(words) < 8:
                re = regex.search(
                    rf'({words}){{e<=1}}', copysong.lyrics.lower())
            else:
                re = regex.search(
                    rf'({words}){{e<=2}}', copysong.lyrics.lower())
            if re is not None:
                start, end = re.span()
                if copysong.lyrics[start:start+2] == "r>":
                    start += 2
                elif copysong.lyrics[start] == ">":
                    start += 1
                copysong.lyrics = copysong.lyrics[:start] + "<mark>" + \
                    copysong.lyrics[start:end] + \
                    "</mark>" + copysong.lyrics[end:]
                query.result.append(copysong)
        query.searched += 1

    db.session.commit()
    return
