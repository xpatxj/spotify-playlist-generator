import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import s_client_id, s_client_secret, redirect_uri, playlist_urll
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

if choice == '1':
    playlist_id, track_ids = get_ids()
    from options import option_one
    option_one(track_ids)

elif choice == '2':
    playlist_id, track_ids = get_ids()
    option = input("Choose an option: 1. BPM 2. Valence 3. Energy. \nType the number of option: ")

    pattern = r"^[123]$"
    match = re.match(pattern, option)

    if match is not None:
        from options import option_two
        option_two(playlist_id, track_ids, option)
    else:
        print("Invalid option. Please choose 1, 2 or 3.")
        exit()
else:
    print("Invalid option. Please choose 1 or 2.")
    exit()