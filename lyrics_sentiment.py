from textblob import TextBlob
import lyricsgenius
from deep_translator import GoogleTranslator

from collections import Counter
from config import g_access_token

genius = lyricsgenius.Genius('g_access_token')

sentiments = []
recommendation_final_playlist = {}
c = []
# do sentiment analysis on song
# def analyze_sentiment(name, artist):
#     try:
#         lyrics = genius.search_song(name, artist).lyrics
#         is_english = GoogleTranslator.detect(lyrics)
#         if is_english != 'english':
#             t_lyrics = GoogleTranslator(source='auto', target='english').translate(lyrics)
#             blob = TextBlob(t_lyrics)
#         else:
#             blob = TextBlob(lyrics)
#         return blob.sentiment.polarity
#     except AttributeError:
#         print("Attribute error")
#         pass
#     except UnboundLocalError:
#         print("Unbound local error")
#         pass
def analyze_sentiment(name, artist):
    try:
        lyrics = genius.search_song(name, artist).lyrics
        blob = TextBlob(lyrics)
        return blob.sentiment.polarity
    except AttributeError:
        print("Attribute error")
        pass
    except UnboundLocalError:
        print("Unbound local error")
        pass
    
# get playlist and do sentiment analysis on each song
def get_playlist(list_of_songs):
    for name, artist in list_of_songs.items():
        try:
            sentiments.append(round(analyze_sentiment(name, artist), 1))
        except TypeError:
            pass
        
    return sentiments


# give recommendations based on sentiment analysis
def get_playlist_recommendations(list_of_songs, sp):
    c = get_most_popular()
    for name, artist in list_of_songs.items():
        if len(recommendation_final_playlist) == 10:
            break
        a = analyze_sentiment(name, artist)
        try:
            s = round(a, 1)
        except TypeError:
            pass
        if s is not None and (s == c[0][0] or s == c[1][0] or s == c[2][0]):
            search = sp.search(q='track:' + name + ' artist:' + artist, type='track')
            try:
                search['tracks']['items'][0]['id']
                recommendation_final_playlist[name] = artist
                print(s)
                print(len(recommendation_final_playlist))
            except IndexError:
                pass
        elif len(recommendation_final_playlist) == 10:
            break
        else:
            pass
        
    return recommendation_final_playlist

#get most popular three songs from playlist
def get_most_popular():
    c = Counter(sentiments).most_common(3)
    return c