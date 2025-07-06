import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic, OAuthCredentials
import time

with open("config.json", "r") as file:
    config = json.load(file)

# ---------- CONFIGURE THESE VARIABLES ----------
SPOTIFY_CLIENT_ID = config["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = config["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI = config["SPOTIFY_REDIRECT_URI"]
SPOTIFY_SCOPE = "playlist-read-private"

YT_CLIENT_ID = config["YT_CLIENT_ID"]
YT_CLIENT_SECRET = config["YT_CLIENT_SECRET"]
# ----------------------------------------------

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SPOTIFY_SCOPE
))

# FORMAT config.json:
# {
#     "SPOTIFY_CLIENT_ID": "API HERE",
#     "SPOTIFY_CLIENT_SECRET": "SECRET HERE",
#     "SPOTIFY_REDIRECT_URI": "http://localhost:8080",
#     "YT_CLIENT_ID": "YT CLIENT API HERE",
#     "YT_CLIENT_SECRET": "YT SECRET HERE"
# }

# Load included playlists from JSON file
with open("playlists.json", "r") as file:
    included_playlists_config = json.load(file)
INCLUDED_PLAYLISTS = set(included_playlists_config.get("included_playlists", []))

# FORMAT playlists.json:
# {
#     "included_playlists": [
#         "spotify:playlist:PLAYLIST CODE HERE"
#     ]
# }

INCLUDED_PLAYLISTS = set(uri.split(":")[-1] for uri in included_playlists_config.get("included_playlists", []))

# Authenticate with YouTube Music
ytmusic = YTMusic('oauth.json', oauth_credentials=OAuthCredentials(client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET))  # Make sure to authenticate via `ytmusicapi oauth` first
def get_spotify_playlists():
    """Fetches the user's Spotify playlists."""
    playlists = sp.current_user_playlists()
    return playlists['items']

def get_playlist_tracks(playlist_id):
    """Fetches tracks from a Spotify playlist."""
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    
    while results:
        tracks.extend(results['items'])
        results = sp.next(results) if results['next'] else None
    
    return [(track['track']['name'], track['track']['artists'][0]['name']) for track in tracks if track['track']]

def search_youtube_music(song, artist):
    """Searches for a song on YouTube Music."""
    query = f"{song} {artist}"
    results = ytmusic.search(query, filter="songs")

    if results:
        return results[0]['videoId']  # Return the first matching video ID
    return None

def create_youtube_playlist(name, description=""):
    """Creates a new playlist on YouTube Music."""
    return ytmusic.create_playlist(name, description)

def add_songs_to_youtube_playlist(playlist_id, video_ids):
    """Adds songs to a YouTube Music playlist."""
    for video_id in video_ids:
        if video_id:
            ytmusic.add_playlist_items(playlist_id, [video_id])
            time.sleep(1)  # Avoid rate limits

def transfer_playlists():
    """Transfers only specified Spotify playlists to YouTube Music."""
    playlists = get_spotify_playlists()

    for playlist in playlists:
        playlist_name = playlist['name']
        playlist_id = playlist['id']

        if playlist_id not in INCLUDED_PLAYLISTS:
            print(f"Skipping playlist: {playlist_name}")
            continue  # Skip playlists not in the included list

        print(f"Transferring playlist: {playlist_name}...")

        # Get tracks from Spotify playlist
        tracks = get_playlist_tracks(playlist_id)
        
        # Search for each song on YouTube Music
        video_ids = [search_youtube_music(song, artist) for song, artist in tracks]

        # Create a YouTube Music playlist
        yt_playlist_id = create_youtube_playlist(playlist_name, playlist.get('description', ""))

        # Add songs to the YouTube Music playlist
        add_songs_to_youtube_playlist(yt_playlist_id, video_ids)

        print(f"Playlist '{playlist_name}' transferred successfully!\n")

# Run the script
transfer_playlists()
