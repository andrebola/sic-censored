#!/usr/bin/env python

from freemuse import FreemuseParser
import pickle
from IPython import embed
import time
import multiprocessing

# TODO: add other countries

map_tiny = {
    'europe': ['spain', 'italy']
}

map_small = {
    'africa': ['cameroon'],
    'europe': ['spain','france']
}

map = {
    'africa': ['angola', 'burkina faso', 'burundi', 'cameroon', 'central african republic', 'comoros', "cote d'ivoire", 'dr congo'],
    'europe': ['austria', 'belarus', 'belgium', 'bosnia and herzegovina', 'croatia', 'czech republic', 'denmark'],
    'asia': ['afghanistan', 'armenia', 'australia', 'azerbaijan', 'bangladesh', 'brunei', 'cambodia'],
    'north-south-america': ['argentina', 'barbados', 'bolivia', 'brazil', 'canada'],
    'middle-east-north-africa': ['algeria', 'bahrain', 'egypt', 'iran']
}

def get_artists(map):
    artists = {}
    inputs = set()
    for region, countries in map.items():
        for country in countries:
            inputs.add((region,country))
            # artists.update(parser.get_artists(region, country))
    tic = time.perf_counter()
    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        res = p.starmap(get_artists, inputs)
    toc = time.perf_counter()
    print("time: {:0.2f}".format(toc-tic))
    return(res)


if __name__ == "__main__":
    parser = FreemuseParser()
    artists = {}
    inputs = set()
    for region, countries in map_tiny.items():
        for country in countries:
            inputs.add((region,country))
            # artists.update(parser.get_artists(region, country))
    tic = time.perf_counter()
    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        res = p.starmap(parser.get_artists, inputs)
    toc = time.perf_counter()
    print("time: {:0.2f}".format(toc-tic))
    print(res)
    embed()
    # try:
    #     fd = open(MAP + '.pkl','wb')
    #     pickle.dump(artists, fd)
    #     fd.close()
    # except Exception as e:
    #     print(e)
