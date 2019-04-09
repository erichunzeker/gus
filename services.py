from googleapiclient.discovery import build
import os, secrets, spotipy, pylast, pprint, deezer, tidalapi
import spotipy.oauth2 as oauth2

spotify_secret = os.environ.get('SPOTIFY_SECRET')
spotify_id = os.environ.get('SPOTIFY_ID')
lastfm_secret = os.environ.get('LASTFM_SECRET')
lastfm_id = os.environ.get('LASTFM_KEY')
deezer_secret = os.environ.get('DEEZER_SECRET')
deezer_id = os.environ.get('DEEZER_ID')
tidal_secret = os.environ.get('TIDAL_PASSWORD')
tidal_id = os.environ.get('TIDAL_LOGIN')
google_id = os.environ.get('GOOGLE_KEY')
soundcloud_id = os.environ.get('CX_SOUNDCLOUD')
pandora_id = os.environ.get('CX_PANDORA')
play_id = os.environ.get('CX_PLAY_MUSIC')

credentials = oauth2.SpotifyClientCredentials(
    client_id=spotify_id,
    client_secret=spotify_secret)

token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)

lastfm = pylast.LastFMNetwork(api_key=lastfm_id, api_secret=lastfm_secret)

deezerClient = deezer.Client()

tidal = tidalapi.Session()
tidal.login(tidal_id, tidal_secret)

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res

def Deezer(type, album, track, artist):
    if type=="album":
        deez = deezerClient.advanced_search({"artist": artist, "album": album}, relation=type)
    elif type=="track":
        deez = deezerClient.advanced_search({"artist": artist, "album": album, "track": track}, relation=type)
    elif type=="artist":
        deez = deezerClient.advanced_search({"artist": artist}, relation=type)
    
    if len(str(deez[0].asdict()['id'])) > 0:
        return type + "/" + str(deez[0].asdict()['id'])
    return ""

def Tidal(type, album, track, artist):
    if type=="album":
        tid = tidal.search('album', album)
        for i in tid.albums:
            if i.name.lower().strip() == album.lower().strip() and i.artist.name.lower().strip() == artist.lower().strip():
                return "album/" + str(i.id)
    elif type=="track":
        tid = tidal.search('track', track)
        for i in tid.tracks:
            if i.name.lower().strip() == track.lower().strip() and i.artist.name.lower().strip() == artist.lower().strip():
                return "track/" + str(i.id)
    elif type=="artist":
        tid = tidal.search('artist', artist)
        for i in tid.artists:
            if i.name.lower().strip() == artist.lower().strip():
                return "artist/" + str(i.id)
            
#NOT supporting type==artist
def Soundcloud(type, album, track, artist):
    if type=="album":
        result = google_search(album + " by " + artist, google_id, soundcloud_id)
        if 'item' in result.keys():
            for i in result['items']:
                if '/sets/' in i['link']:
                    return i['link'][23:]
    elif type=="track":
        result = google_search(track + " by " + artist, google_id, soundcloud_id)
        if 'item' in result.keys():
            for i in result['items']:
                return i['link'][23:]
    return ""
    
def Pandora(type, album, track, artist):
    if type=="album" or type=="track":
        result = google_search(track + " by " + artist, google_id, pandora_id)
    elif type=="artist":
        result = google_search(artist, google_id, pandora_id)
    if 'item' in result.keys():
        for i in result['items']:
            return i['link'][31:]
    return ""
            
    
def Play(type, album, track, artist):
    if type=="album" or type=="track":
        result = google_search(album + " by " + artist, google_id, play_id)
    elif type=="artist":
        result = google_search(artist, google_id, play_id)
    
    if 'item' in result.keys():
        for i in result['items']:
            if 'https://play.google.com/store/music/' in i['link']:
                return i['link'][36:]
    return ""
        
def get_services(type, album, track, artist):
    #define dict : streaming_service --> URL_for_music
    services = {'lstfm':"#", 'deez':"#", 'tide':"#", 'soundcloud':"#", 'pandora':"#", 'play':"#"}
    if type=="album":
        services['lstfm'] = lastfm.get_album(artist, album).get_url()[26:]
    elif type=="track":
        services['lstfm'] = lastfm.get_track(artist, track).get_url()[26:]
    elif type=="artist":
        services['lstfm'] = lastfm.get_artist(artist).get_url()[26:]

    services['deez'] = Deezer(type, album, track, artist)
    services['tide'] = Tidal(type, album, track, artist)
    services['soundcloud'] = Soundcloud(type, album, track, artist)
    services['pandora'] = Pandora(type, album, track, artist)
    services['play'] = Play(type, album, track, artist)
    print(services)
    return services
