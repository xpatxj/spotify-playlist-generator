from textblob import TextBlob 
import lyricsgenius
from langdetect import detect
from deep_translator import GoogleTranslator
from config import headers
import deep_translator

from collections import Counter
from config import g_access_token 
import json
import requests

genius = lyricsgenius.Genius('g_access_token')

sentiments = []
recommendation_final_playlist = {}
c = []


# def analyze_sentiment(name, artist):
#     try:
#         lyrics = genius.search_song(name, artist).lyrics
#         detected_language = detect(lyrics)

#         if detected_language != 'en':
            # if len(lyrics) > 5000:
            #     lyrics = lyrics[:5000]
            #     lyrics = GoogleTranslator(source=detected_language, target='english').translate(lyrics)
            # else:
            #     lyrics = GoogleTranslator(source=detected_language, target='english').translate(lyrics)

#         headers = headers

#         url ="https://api.edenai.run/v2/text/sentiment_analysis"
#         payload={
#             "show_original_response": False,
#             "fallback_providers": "",
#             "providers": "google,amazon",
#             'language': "en",
#             'text': lyrics
#         }

#         response = requests.post(url, json=payload, headers=headers)
#         result = json.loads(response.text)
#         items = result['google']['items']
#         print(items)

#         total_sentiment_rate = 0
#         for item in items:
#             sentiment_rate = item['sentiment_rate']
#             if item['sentiment'] == 'Negative':
#                 sentiment_rate = -sentiment_rate
#             else:
#                 sentiment_rate = sentiment_rate
#             total_sentiment_rate += sentiment_rate
#         average_sentiment_rate = total_sentiment_rate / len(items)
#         return average_sentiment_rate
#     except AttributeError:
#         print("Attribute error")
#         pass
#     except UnboundLocalError:
#         print("Unbound local error")
#         pass
#     except KeyError:
#         print("Key error")
#         pass
#     except GoogleTranslator.exceptions.NotValidLengthError:
#         print("Not valid payload error")
#         pass
  
# do sentiment analysis on song
def analyze_sentiment(name, artist):
    try:
        lyrics = genius.search_song(name, artist).lyrics
        detected_language = detect(lyrics)

        if detected_language != 'en':
            if len(lyrics) > 5000:
                lyrics = lyrics[:4999]
                lyrics = GoogleTranslator(source=detected_language, target='english').translate(lyrics)
            else:
                lyrics = GoogleTranslator(source=detected_language, target='english').translate(lyrics)

        blob = TextBlob(lyrics)
        print(blob.sentiment.polarity)
        return blob.sentiment.polarity
    except AttributeError:
        print("Attribute error")
        pass
    except UnboundLocalError:
        print("Unbound local error")
        pass
    except deep_translator.exceptions.NotValidLengthError:
        print("Not valid payload error")
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
        else:
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