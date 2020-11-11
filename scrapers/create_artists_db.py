#!/usr/bin/env python
from freemuse import get_artists_from_freemuse
from IPython import embed

# TODO: add other countries

map_small = {
    'africa': ['angola'],
    'europe': ['spain','france']
}

map = {
    'africa': ['angola', 'burkina faso', 'burundi', 'cameroon', 'central african republic', 'comoros', "cote d'ivoire", 'dr congo'],
    'europe': ['austria', 'belarus', 'belgium', 'bosnia and herzegovina', 'croatia', 'czech republic', 'denmark'],
    'asia': ['afghanistan', 'armenia', 'australia', 'azerbaijan', 'bangladesh', 'brunei', 'cambodia'],
    'north-south-america': ['argentina', 'barbados', 'bolivia', 'brazil', 'canada'],
    'middle-east-north-africa': ['algeria', 'bahrain', 'egypt', 'iran']
}

artists = {}

for region, countries in map_small.items():
    for country in countries:
         artists.update(get_artists_from_freemuse(region, country))

embed()