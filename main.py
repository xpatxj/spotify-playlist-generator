import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import s_client_id, s_client_secret, redirect_uri, playlist_urll
from lyrics_sentiment import get_playlist, get_most_popular, get_playlist_recommendations, recommendation_final_playlist
import matplotlib.pyplot as plt
import re

scope = 'playlist-read-private playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=s_client_id, client_secret=s_client_secret, redirect_uri=redirect_uri, scope=scope))

user_info = sp.current_user()
user_id = user_info['id']

# playlist_urll = input("Please enter URL of playlist: ")
chose = input("""Choose an option: 
            1. 10 new tracks recommendation based on playlist's songs' lyrics' sentiment analysis.
            2. Chart based on your playlist: BPM, velance, energy.\n""")

def is_valid_spotify_url(url):
    pattern = r"https://open\.spotify\.com/playlist/[a-zA-Z0-9]+(\?si=[a-zA-Z0-9]+)?"
    match = re.match(pattern, url)
    return match is not None

def get_ids():

    if is_valid_spotify_url(playlist_urll) == True:
        playlist_url = playlist_urll.split('?')[0]
        playlist_id = playlist_url.split('/')[-1]

        tracks = sp.playlist_tracks(playlist_id)
        
        track_ids = [track['track']['id'] for track in tracks['items']]

        if track_ids == [None]:
            print("No tracks found. Please make sure playlist is not empty.")
            exit()
        else:
            return track_ids
    else:
        print("Invalid URL. Please make sure URL looks like this: https://open.spotify.com/playlist/[id]?si=[random_string]")
        exit()
    

def option_one(track_ids):

    tracks_info = {}
    for track_id in track_ids:
        track = sp.track(track_id)
        artists = ', '.join([artist['name'] for artist in track['artists']])
        tracks_info[track['name']] = artists

    print(tracks_info)
    get_playlist(tracks_info)
    get_most_popular()
    print(get_most_popular())

    seed_tracks = track_ids[:5]
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=30)

    recommendations_ids = [track['id'] for track in recommendations['tracks']]
    recommendations_info = {}
    for r_id in recommendations_ids:
        track = sp.track(r_id)
        artists = ', '.join([artist['name'] for artist in track['artists']])
        recommendations_info[track['name']] = artists

    get_playlist_recommendations(recommendations_info, sp)
    # print(recommendations_info)
    # print(recommendation_final_playlist)

    name = input("Please enter name of playlist: ")
    new_playlist = sp.user_playlist_create(user=user_id, name=name, public=True, description='recommended songs based on playlist')

    for name, artist in recommendation_final_playlist.items():
        search = sp.search(q='track:' + name + ' artist:' + artist, type='track')
        try:
            track_id = search['tracks']['items'][0]['id']
            sp.playlist_add_items(playlist_id=new_playlist['id'], items=[track_id])
            print(f"track {name} by {artist} added to playlist")
        except IndexError:
            print("Index error")

def option_two(track_ids, option):
    
    features = []
    name_of_feature = ''

    if option == '1':
        for track_id in track_ids:
            audio_features = sp.audio_features([track_id])[0]
            features.append(round(audio_features['tempo']))
        name_of_feature = 'BPM'
    
    if option == '2':
        for track_id in track_ids:
            audio_features = sp.audio_features([track_id])[0]
            features.append(audio_features['valence'])
        name_of_feature = 'valence'

    if option == '3':
        for track_id in track_ids:
            audio_features = sp.audio_features([track_id])[0]
            features.append(audio_features['energy'])
        name_of_feature = 'energy'
    
    color = get_dominant_color(user_info['images'][0]['url'])

    plt.hist(features, bins=range(min(features), max(features) + 4, 4), color=color, edgecolor='black')

    plt.xlabel(name_of_feature)
    plt.ylabel('count')

    plt.show()

# def option_three():
#     print("option three")

def get_dominant_color(url):

    from PIL import Image
    import requests
    from io import BytesIO

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    img = img.resize((1, 1))

    dominant_color = img.getpixel((0, 0))

    color = '#{:02x}{:02x}{:02x}'.format(*dominant_color)

    return color

if chose == '1':
    track_ids = get_ids()
    option_one(track_ids)

elif chose == '2':
    track_ids = get_ids()
    option = input("Choose an option: 1. BPM 2. Valence 3. Energy. \nType the number of option: ")
    option_two(track_ids, option)

# elif chose == '3':
#     option_three()