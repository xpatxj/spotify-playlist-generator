from textblob import TextBlob
import lyricsgenius

from collections import Counter
from config import g_access_token

genius = lyricsgenius.Genius('g_access_token')
sentiments = []
recommendation_final_playlist = {}
c = []

# do sentiment analysis on song
def analyze_sentiment(name, artist):
    try:
        lyrics = genius.search_song(name, artist).lyrics
        blob = TextBlob(lyrics)
        return blob.sentiment.polarity
    except AttributeError:
        pass
    except UnboundLocalError:
        pass
    

# get playlist and do sentiment analysis on each song
def get_playlist(list_of_songs):
    for name, artist in list_of_songs.items():
        sentiments.append(round(analyze_sentiment(name, artist), 1))
    return sentiments



def get_playlist_recommendations(list_of_songs):
    
    for name, artist in list_of_songs.items():
        s = round(analyze_sentiment(name, artist), 1)
        if s is not None and (s == 0.2 or s == 0.1 or s == 0.3):
            recommendation_final_playlist[name] = artist
            print(s)
        elif len(recommendation_final_playlist) >= 10:
            break
        else:
            pass
        
    return recommendation_final_playlist

#get most popular three songs from playlist
def get_most_popular():
    c = Counter(sentiments).most_common(3)
    return c