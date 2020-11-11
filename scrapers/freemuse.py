#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import spacy
import musicbrainzngs
import pycountry
import spotipy
import os
import json
import argparse
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy.util as util
from musixmatch_scraper import Musixmatch
from Levenshtein.StringMatcher import StringMatcher

from IPython import embed

ID = os.environ.get('SPOTIFY_ID')
SECRET = os.environ.get('SPOTIFY_SECRET')
REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=ID, client_secret=SECRET))
scope = 'playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=ID,
                                               client_secret=SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

musicbrainzngs.set_useragent("sic-censored", "0.1", "http://example.com")
nlp = spacy.load("en_core_web_sm")


def get_args():
    parser = argparse.ArgumentParser(description='test freemuse=>musicbrainz=>spotify')
    # TODO: just pass country and map region
    parser.add_argument('-r', '--region', required=True, default='europe',
                        help='europe/africa/asia/north-south-america/middle-east-north-africa')
    parser.add_argument('-c', '--country', required=True, default='spain',
                        help='country')
    return parser.parse_args()


def get_artists_from_freemuse(region, country):
    country = country.lower()
    artists = set()
    # TODO: parse through all pages not just first one
    url = "https://freemuse.org/regions" + "/" + region + "/" + country
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    items = soup.find_all(class_="item-list")
    for item in items:

        entry_title  = item.find(class_="post-box-title")
        entry = item.find(class_="entry")
        
        title = entry_title.find('a').getText()
        article = entry.find('p').getText()

        doc = nlp(f'{title}. {article}')
        # keep only persons 
        # TODO: sometimes actually ORG is relevant too
        entities = [x.text for x in doc.ents if ((x.label_ == 'PERSON') | (x.label_ == 'ORG'))]
        # entities2 = [x.text for x in doc.ents if (x.label_ == 'ORG')]
        country_iso = pycountry.countries.get(name=country).alpha_2
        if entities:
            for entity in set(entities):
                # cross check person with musicbrainz so we make sure the artist exists in the specified country
                # TODO: not very robust. find some way to double check
                try:
                    query = musicbrainzngs.search_artists(artist=entity, country=country_iso)
                    artist_in_musicbrainz = query['artist-list'][0]['name']
                    print(query['artist-list'][0]['country'], query['artist-list'][0]['name'], entity)
                    dist_artist = StringMatcher(seq1=artist_in_musicbrainz.lower(), seq2=entity.lower()).distance()
                    # A higher value will allow to match different artists, I think between 5 and 10 should be a good range.
                    if dist_artist < 5 and (query['artist-list'][0]['country'] == country_iso):
                        artists.add(artist_in_musicbrainz)
                        print(f'Success! Found artist {entity}')
                    else:
                        print(f'Found name {entity} but not in Musicbrainz, closest artists is {artist_in_musicbrainz} with distance {dist_artist}')
                except:
                    print(f'Something failed for {entity}')
                    pass
    return(artists)


if __name__ == "__main__":

    args = get_args()
    artists = get_artists_from_freemuse(args.region, args.country)
    print(artists)


