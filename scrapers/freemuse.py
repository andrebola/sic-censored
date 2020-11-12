#!/usr/bin/env python
# 11/05/20 sylvain // telegram: @slegroux

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


def get_args():
    parser = argparse.ArgumentParser(description='test freemuse=>musicbrainz=>spotify')
    # TODO: just pass country and map region
    parser.add_argument('-r', '--region', required=True, default='europe',
                        help='europe/africa/asia/north-south-america/middle-east-north-africa')
    parser.add_argument('-c', '--country', required=True, default='spain',
                        help='country')
    return parser.parse_args()


class FreemuseParser():
    def __init__(self):
        musicbrainzngs.set_useragent("sic-censored", "0.1", "http://example.com")
        self._nlp = spacy.load("en_core_web_sm")
        
    def get_artists(self, region, country, number_pages=4):
        country = country.lower()
        country_iso = pycountry.countries.get(name=country).alpha_2
        artists = set()

        for page_number in range(1,number_pages+1):
            url = "https://freemuse.org/regions" + "/" + region + "/" + country + "/page/" + str(page_number)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            items = soup.find_all(class_="item-list")
            for item in items:
                entry_title  = item.find(class_="post-box-title")
                entry = item.find(class_="entry")
                title = entry_title.find('a').getText()
                article = entry.find('p').getText()
                doc = self._nlp(f'{title}. {article}')
                # sometimes actually ORG is relevant too
                entities = [x.text for x in doc.ents if ((x.label_ == 'PERSON') | (x.label_ == 'ORG'))]
                if entities:
                    for entity in set(entities):
                        # cross check person with musicbrainz so we make sure the artist exists in the specified country
                        # TODO: not very robust. find some way to double check
                        try:
                            query = musicbrainzngs.search_artists(artist=entity, country=country_iso)
                            artist_in_musicbrainz = query['artist-list'][0]['name']
                            dist_artist = StringMatcher(seq1=artist_in_musicbrainz.lower(), seq2=entity.lower()).distance()
                            if (dist_artist < 5 and query['artist-list'][0]['country'] == country_iso):
                                artists.add(artist_in_musicbrainz)
                                print(f'Success! Found artist {entity}')
                            else:
                                print(f'Found name {entity} but not in Musicbrainz, closest artists is {artist_in_musicbrainz}')
                        except Exception as e:
                            print(f'Something failed for {entity}', e)
        return({country_iso: list(artists)})


if __name__ == "__main__":
    args = get_args()
    parser = FreemuseParser()
    artists = parser.get_artists(args.region, args.country)
    print(artists)


