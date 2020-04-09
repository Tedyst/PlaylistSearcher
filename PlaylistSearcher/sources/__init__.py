import PlaylistSearcher.sources.genius as genius
import PlaylistSearcher.sources.youtube as youtube
from PlaylistSearcher import Song
import time
from PlaylistSearcher import APP, db

SOURCES = [genius, youtube]


def update_lyrics(song: Song):
    for source in SOURCES:
        lyrics = source.get_lyrics(song)
        if lyrics is not None:
            song.lyrics = lyrics.replace('\n', '<br>')
            APP.logger.info("Taken lyrics for %s from %s",
                            song.title, source.SOURCE_NAME)
            song.last_check = int(time.time())
            db.session.add(song)
            return

    song.last_check = int(time.time())
    APP.logger.info("Did not find any lyrics for %s",
                    song.title)
    return
