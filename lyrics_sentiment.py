from textblob import TextBlob
import lyricsgenius

from collections import Counter
from config import g_access_token

genius = lyricsgenius.Genius('g_access_token')
sentiments = []

# do sentiment analysis on song
def analyze_sentiment(name, artist):
    try:
        lyrics = genius.search_song(name, artist).lyrics
        blob = TextBlob(lyrics)
    except AttributeError:
        pass
    return blob.sentiment.polarity

# get playlist and do sentiment analysis on each song
def get_playlist(list_of_songs):
    for name, artist in list_of_songs.items():
        # sentiments.append(round(analyze_sentiment(name, artist), 1))
        sentiments.append(analyze_sentiment(name, artist))
    return sentiments

#get most popular three songs from playlist
def get_most_popular():
    c = Counter(sentiments).most_common(3)
    return c