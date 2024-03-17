import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API credentials
SPOTIPY_CLIENT_ID = '5cc2c5e1cb89415691101bab9c04ecad'
SPOTIPY_CLIENT_SECRET = '58d2f8972c094e94a49eeff8eb19408c'

# Spotify API authentication
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

def get_top_songs(artist_name):
    try:
        results = sp.search(q=f'artist:{artist_name}', type='artist')
        if results['artists']['items']:
            artist_id = results['artists']['items'][0]['id']
            top_tracks = sp.artist_top_tracks(artist_id)
            
            st.sidebar.subheader(f"Top 5 Songs by {artist_name}")
            
            for track in top_tracks['tracks'][:5]:
                st.sidebar.write(f"**{track['name']}**")
                
                # Select the largest available image, if it exists
                image_url = next((image['url'] for image in track['album']['images'] if image['height'] == max(image['height'] for image in track['album']['images'])), None)
                
                if image_url:
                    st.sidebar.image(image_url, caption=track['album']['name'], use_column_width=True, output_format="auto")
                else:
                    st.sidebar.write("No high-resolution image available.")
        else:
            st.sidebar.write(f"No artist found with the name {artist_name}")

    except Exception as e:
        st.sidebar.write(f"Error getting top songs: {e}")