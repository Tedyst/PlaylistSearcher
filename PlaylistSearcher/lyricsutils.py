from PlaylistSearcher import APP, Song


def search_words(list_of_songs, words):
    result = []
    for song in list_of_songs:
        if type(song) != Song:
            continue
