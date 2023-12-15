import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import s_client_id, s_client_secret, redirect_uri, playlist_url
from lyrics_sentiment import get_playlist, get_most_popular


scope = 'playlist-read-private playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=s_client_id, client_secret=s_client_secret, redirect_uri=redirect_uri, scope=scope))

user_info = sp.current_user()
user_id = user_info['id']

# playlist_url = input("Please enter URL of playlist: ")

playlist_url = playlist_url.split('?')[0]
playlist_id = playlist_url.split('/')[-1]

tracks = sp.playlist_tracks(playlist_id)

tracks_info = {}
track_ids = [track['track']['id'] for track in tracks['items']]

# for track_id in track_ids:
#     track = sp.track(track_id)
#     artists = ', '.join([artist['name'] for artist in track['artists']])
#     tracks_info[track['name']] = artists

# sentiment = get_playlist(tracks_info)
# most_common = get_most_popular()
# print("The most popular sentiment in this playlist is: " + str(most_common))
# print(sentiment)

# new_playlist = sp.user_playlist_create(user=user_id, name='recommended<3', public=True, description='recommended songs based on playlist')

seed_tracks = track_ids[:5]

recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=20)
print(recommendations)

# track_uris = [track['uri'] for track in recommendations['tracks']]
# sp.playlist_add_items(new_playlist['id'], track_uris)
