import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from auth import CLIENT_ID, CLIENT_SECRET

# SPOTIFY AUTHENTICATION
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                          client_id=CLIENT_ID,
                          client_secret=CLIENT_SECRET,
                          redirect_uri="http://localhost:8888/callback",
                          scope="playlist-modify-private",
                          cache_path="token.txt"))
user_id = sp.current_user()["id"]

# INPUT
date = input("What year do you want to be musically time-traveled to? Write it format YYY-MM-DD: \n")
year = date.split("-")[0]

# WEB SCRAPPING
response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}/")

billboard_html = response.text
response.raise_for_status()

soup = BeautifulSoup(billboard_html, "html.parser")
song_names_spans = soup.find_all("h3", class_="a-no-trucate")
song_names = [song.getText(strip=True) for song in song_names_spans]

# ADDING THE FOUND SONGS ONTO A LIST
song_uri = []
for song in song_names:

    result = sp.search(q=f"track: {song}, year: {year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uri.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
print(playlist)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uri)
