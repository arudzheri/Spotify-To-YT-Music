import spotipy
import json
import time
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic, OAuthCredentials

# Load configuration
with open("config.json", "r") as file:
    config = json.load(file)

# ---------- CONFIGURE THESE VARIABLES ----------
SPOTIFY_CLIENT_ID = config["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = config["SPOTIFY_CLIENT_SECRET"]
SPOTIFY_REDIRECT_URI = config["SPOTIFY_REDIRECT_URI"]
SPOTIFY_SCOPE = "user-library-read"

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

# Authenticate with YouTube Music
ytmusic = YTMusic('oauth.json', oauth_credentials=OAuthCredentials(client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET))

def get_spotify_liked_songs():
    """Fetches the user's liked songs from Spotify."""
    tracks = []
    results = sp.current_user_saved_tracks()
    
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

def like_song_on_youtube(video_id):
    """Likes a song on YouTube Music."""
    if video_id:
        ytmusic.rate_song(video_id, "LIKE")
        time.sleep(1)  # Avoid rate limits

def transfer_liked_songs():
    """Transfers liked songs from Spotify to YouTube Music."""
    print("Fetching liked songs from Spotify...")
    liked_songs = get_spotify_liked_songs()
    print(f"Found {len(liked_songs)} liked songs.")
    
    for song, artist in liked_songs:
        print(f"Searching for: {song} - {artist} on YouTube Music...")
        video_id = search_youtube_music(song, artist)
        
        if video_id:
            print(f"Liking song: {song} - {artist} on YouTube Music...")
            like_song_on_youtube(video_id)
        else:
            print(f"Could not find: {song} - {artist} on YouTube Music.")
    
    print("Transfer complete!")

# Run the script
transfer_liked_songs()
