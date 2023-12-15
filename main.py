import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import s_client_id, s_client_secret, redirect_uri, playlist_url
from lyrics_sentiment import get_playlist, get_most_popular, get_playlist_recommendations, recommendation_final_playlist

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

get_playlist_recommendations(recommendations_info)
print(recommendations_info)
print(recommendation_final_playlist)

new_playlist = sp.user_playlist_create(user=user_id, name='recommended<3', public=True, description='recommended songs based on playlist')

for name, artist in recommendation_final_playlist.items():
    search = sp.search(q='track:' + name + ' artist:' + artist, type='track')
    try:
        track_id = search['tracks']['items'][0]['id']
        sp.playlist_add_items(playlist_id=new_playlist['id'], items=[track_id])
        print(f"track {name} by {artist} added to playlist")
    except IndexError:
        print("Index error")
