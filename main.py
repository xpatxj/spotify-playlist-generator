import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import s_client_id, s_client_secret, redirect_uri
from lyrics_sentiment import get_playlist, get_most_popular, get_playlist_recommendations, recommendation_final_playlist
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
import io
import base64
import re
import requests
from requests.exceptions import Timeout
import numpy as np
import matplotlib
matplotlib.use('Agg')

scope = 'playlist-read-private playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=s_client_id, client_secret=s_client_secret, redirect_uri=redirect_uri, scope=scope))

user_info = sp.current_user()
user_id = user_info['id']

app = Flask(__name__)

def get_dominant_colors(url):

        from PIL import Image
        import requests
        from io import BytesIO
        from sklearn.cluster import KMeans

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

@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    error = None
    playlist_urll = request.form.get('url')
    option = request.form.get('option')
    choice = request.form.get('choose')
    if request.method == 'POST':
        track_ids = []
    
        if not re.match(r"https://open\.spotify\.com/playlist/[a-zA-Z0-9]+(\?si=[a-zA-Z0-9]+)?", playlist_urll):
            error = 'URL is invalid. Please make sure URL is a valid Spotify playlist URL.'
        else:
            playlist_url = playlist_urll.split('?')[0]
            playlist_id = playlist_url.split('/')[-1]

            tracks = sp.playlist_tracks(playlist_id)
            
            track_ids = [track['track']['id'] for track in tracks['items']]

            if track_ids == [None]:
                error = 'No tracks found. Please make sure playlist is not empty.'
            if choice == '1':
                tracks_info = {}
                for track_id in track_ids:
                    track = sp.track(track_id)
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    tracks_info[track['name']] = artists

                get_playlist(tracks_info)
                get_most_popular()

                seed_tracks = track_ids[:5]
                try:
                    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=30)

                    recommendations_ids = [track['id'] for track in recommendations['tracks']]
                    recommendations_info = {}
                    for r_id in recommendations_ids:
                        track = sp.track(r_id)
                        artists = ', '.join([artist['name'] for artist in track['artists']])
                        recommendations_info[track['name']] = artists

                    get_playlist_recommendations(recommendations_info, sp)

                    name = request.form.get('playlistName')
                    new_playlist = sp.user_playlist_create(user=user_id, name=name, public=True, description='recommended songs based on playlist')

                    for name, artist in recommendation_final_playlist.items():
                        search = sp.search(q='track:' + name + ' artist:' + artist, type='track')
                        
                        track_id = search['tracks']['items'][0]['id']
                        sp.playlist_add_items(playlist_id=new_playlist['id'], items=[track_id])
                    error = 'Playlist created successfully!'
                except IndexError:
                    error = 'Something went wrong. Please try again later.'
                except Timeout:
                    error = 'Request timed out. Please try again later.'

            
            elif choice == '2':
                bpms = []
                valences = []
                energies = []
                name_of_feature = ''
                image_url = sp.playlist(playlist_id)['images'][0]['url']

                colors = get_dominant_colors(image_url)

                if option == '1':
                    for track_id in track_ids:
                        audio_features = sp.audio_features([track_id])[0]
                        bpms.append(round(audio_features['tempo']))
                    name_of_feature = 'BPM'
                    bins = range(min(bpms), max(bpms) + 2)

                    for i in range(len(bins)-1):
                        plt.hist([f for f in bpms if bins[i] <= f < bins[i+1]], bins=[bins[i], bins[i+1]], color=colors[i%len(colors)], edgecolor='black')
                
                elif option == '2':
                    
                    for track_id in track_ids:
                        audio_features = sp.audio_features([track_id])[0]
                        valences.append(audio_features['valence'])
                    name_of_feature = 'valence'
                    bins = np.arange(min(valences), max(valences)+ 0.2, 0.1)

                    for i in range(len(bins)-1):
                        plt.hist(valences, bins=bins[i:i+2], color=colors[i%len(colors)], edgecolor='black')

                elif option == '3':
                    
                    for track_id in track_ids:
                        audio_features = sp.audio_features([track_id])[0]
                        energies.append(audio_features['energy'])
                    name_of_feature = 'energy'
                    bins = np.arange(min(energies), max(energies)+ 0.2, 0.1)

                    for i in range(len(bins)-1):
                        plt.hist(energies, bins=bins[i:i+2], color=colors[i%len(colors)], edgecolor='black')
                else:
                    error = 'Please choose an option.'

                plt.xlabel(name_of_feature)
                plt.ylabel('count')
                energies.clear()
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                plt.clf()
                

    return render_template('index.html', error=error, plot_url=plot_url)
    
if __name__ == '__main__':
    app.run(debug=True)