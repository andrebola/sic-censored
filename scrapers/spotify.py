#!/usr/bin/env python

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy.util as util
import os
import argparse

ID = os.environ.get('SPOTIFY_ID')
SECRET = os.environ.get('SPOTIFY_SECRET')
REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')


def get_args():
    parser = argparse.ArgumentParser(description='create playlist')
    parser.add_argument('-p', '--playlist_name', required=True, default='test',
                        help='playlist name')
    parser.add_argument('-a', '--artist', required=True, default='rosalia',
                        help='artist name')
    return parser.parse_args()


class SpotifyPlaylistGenerator(object):
    def __init__(self, playlist_name='sic-censored'):
        scope = 'playlist-modify-public'
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=ID,
                                               client_secret=SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))
        self.playlist_name = playlist_name
        self.playlist = None

    def top_tracks(self, artist):
        ret = self.sp.search(artist)
        if len(ret['tracks']['items']):
            uri = ret['tracks']['items'][0]['artists'][0]['uri']
            response = self.sp.artist_top_tracks(uri)
            return(response['tracks'])
        return []

    def create_playlist(self, playlist_name='sic-censored'):
        self.playlist_name = playlist_name
        user_id = self.sp.me()['id']
        self.pl = self.sp.user_playlist_create(user_id, self.playlist_name)
    
    def add_to_playlist(self, tids):
        self.sp.playlist_add_items(self.pl['id'], tids)


if __name__ == "__main__":
    args = get_args()
    pl = SpotifyPlaylistGenerator()
    res = pl.top_tracks(args.artist)
    pl.create_playlist(args.playlist_name)
    pl.add_to_playlist([x['id'] for x in res])
