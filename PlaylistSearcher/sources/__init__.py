import PlaylistSearcher.sources.genius as genius
import PlaylistSearcher.sources.youtube as youtube
from PlaylistSearcher import Song
import time
from PlaylistSearcher import APP, db
from queue import Queue

SOURCES = [genius]


def update_lyrics_queue(q: Queue, song: Song, copysong: Song):
    update_lyrics(song)
    q.put([song, copysong])


def update_lyrics(song: Song):
    for source in SOURCES:
        if source.SOURCE_NAME == song.source:
            return
        # Check only once per day
        if song.last_check:
            if time.time() - song.last_check < 86400:
                return
        lyrics = source.get_lyrics(song)
        if lyrics is not None:
            song.lyrics = lyrics.replace('\n', '<br>')
            APP.logger.info("Taken lyrics for %s from %s",
                            song.title, source.SOURCE_NAME)
            song.source = source.SOURCE_NAME
            song.last_check = int(time.time())
            return

    song.last_check = int(time.time())
    APP.logger.info("Did not find any lyrics for %s",
                    song.title)
    return
