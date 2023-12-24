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
choice = input("""Choose an option: 
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
            return playlist_id, track_ids
    else:
        print("Invalid URL. Please make sure URL looks like this: https://open.spotify.com/playlist/[id]?si=[random_string]")
        exit()
    

def option_one(track_ids):

    tracks_info = {}
    for track_id in track_ids:
        track = sp.track(track_id)
        artists = ', '.join([artist['name'] for artist in track['artists']])
        tracks_info[track['name']] = artists

    # print(tracks_info)
    get_playlist(tracks_info)
    get_most_popular()
    # print(get_most_popular())

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

def option_two(playlist_id, track_ids, option):
    
    features = []
    name_of_feature = ''

    if option == '1':
        for track_id in track_ids:
            audio_features = sp.audio_features([track_id])[0]
            features.append(round(audio_features['tempo']))
        name_of_feature = 'BPM'
        print("""The overall estimated tempo of a track in beats per minute (BPM). 
        In musical terminology, tempo is the speed or pace of a given piece and derives directly 
        from the average beat duration.""")
    
    if option == '2':
        for track_id in track_ids:
            audio_features = sp.audio_features([track_id])[0]
            features.append(audio_features['valence'])
        name_of_feature = 'valence'
        print("""Valence is a measure describing the musical positiveness conveyed by a track. 
        Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with 
        low valence sound more negative (e.g. sad, depressed, angry)""")

    if option == '3':
        for track_id in track_ids:
            audio_features = sp.audio_features([track_id])[0]
            features.append(audio_features['energy'])
        name_of_feature = 'energy'
        print("""Energy is a measure that represents a perceptual measure of intensity 
        and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, 
        death metal has high energy, while a Bach prelude scores low on the scale. Perceptual 
        features contributing to this attribute include dynamic range, perceived loudness, timbre, 
        onset rate, and general entropy""")

    import numpy as np

    image_url = sp.playlist(playlist_id)['images'][0]['url']

    colors = get_dominant_colors(image_url)
    
    if option == '1':
        bins = range(min(features), max(features), 1)

        for i in range(len(bins)-1):
            plt.hist([f for f in features if bins[i] <= f < bins[i+1]], bins=[bins[i], bins[i+1]], color=colors[i%len(colors)], edgecolor='black')
    else:
        bins = np.arange(min(features), max(features), 0.1)

        for i in range(len(bins)-1):
            plt.hist(features, bins=bins[i:i+2], color=colors[i%len(colors)], edgecolor='black')

    plt.xlabel(name_of_feature)
    plt.ylabel('count')

    plt.show()

def get_dominant_colors(url):

    from PIL import Image
    import requests
    from io import BytesIO
    from sklearn.cluster import KMeans
    import numpy as np

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((50, 50)) 
    pixels = np.array(img).reshape(-1, 3)

    n_colors = 3
    kmeans = KMeans(n_clusters=n_colors)  
    kmeans.fit(pixels)

    counts = np.bincount(kmeans.labels_)
    sorted_colors = kmeans.cluster_centers_[np.argsort(-counts)]

    colors = ['#{:02x}{:02x}{:02x}'.format(int(color[0]), int(color[1]), int(color[2])) for color in sorted_colors]

    return colors

if choice == '1':
    playlist_id, track_ids = get_ids()
    option_one(track_ids)

elif choice == '2':
    playlist_id, track_ids = get_ids()
    option = input("Choose an option: 1. BPM 2. Valence 3. Energy. \nType the number of option: ")

    pattern = r"^[123]$"
    match = re.match(pattern, option)

    if match is not None:
        option_two(playlist_id, track_ids, option)
    else:
        print("Invalid option. Please choose 1, 2 or 3.")
        exit()
else:
    print("Invalid option. Please choose 1 or 2.")
    exit()