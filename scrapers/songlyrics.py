#!/usr/bin/env python

import urllib
import lxml.html
from urllib.request import urlopen, Request
import json
import pprint
import time
import argparse
import unicodedata
from Levenshtein.StringMatcher import StringMatcher

class Songlyrics(object):
    def _remove_accents(self, input_str):
        nkfd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

    def _search(self, artist, title=None):
        artist = self._remove_accents(artist.lower())
        if title != None:
            search = urllib.parse.quote_plus("%s %s" % (artist, title))
        else:
            search = urllib.parse.quote_plus(artist.encode('utf-8'))
        url = u'http://www.songlyrics.com/index.php?section=search&searchW=%s&submit=Search&searchIn1=artist&searchIn3=song' % search
        user_agent = "(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        headers={'User-Agent' : user_agent}
        req = Request(url, headers=headers)
        content = urlopen(req)
        page = lxml.html.parse(content)
        links = page.getroot().cssselect('.serpresult')
        resp = []
        #search_original = u"%s - %s" % (artist.lower(), title.lower())
        if len(links):
            for link in links:
                current_song = link.cssselect('h3>a')
                if len(current_song) and current_song[0].text != None:
                    song_title = current_song[0].text.replace('Lyrics', '')
                    song_artist = link.cssselect('.serpdesc-2>p>a')[0].text

                    search = u"%s - %s" % (song_artist.lower(), song_title.lower())
                    dist_artist = StringMatcher(seq1=artist.lower(), seq2=song_artist.lower()).distance()
                    dist_title = 0
                    if title != None:
                        dist_title =  StringMatcher(seq1=title.lower(), seq2=song_title.lower()).distance()
                    #print (dist_artist, artist, song_artist)
                    #print (title, dist_title)
                    if dist_artist < 5 and (title!=None or dist_title < 10):
                        resp.append(current_song[0].get('href'))
        return resp

    def get_data(self, artist, title=None):
        urls = self._search(artist, title)
        print ("Found {} tracks for {}, start collecting each track...".format(len(urls), artist))
        ret = []
        for url in urls:
            lyr = self._get_lyrics_from_url(url)
            if lyr:
                ret.append(lyr)
        return ret

    def _get_lyrics_from_url(self, url):
        #print (url)
        user_agent = "(X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        headers={'User-Agent' : user_agent}
        req = Request(url, headers=headers)
        content = urlopen(req)
        page = lxml.html.parse(content)
        div = page.getroot().get_element_by_id('songLyricsDiv')
        text = ''.join([text for text in div.itertext()])
        return text


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Download lyrics.')
    parser.add_argument('--artist', dest='artist')
    args = parser.parse_args()
    source = Songlyrics()
    ret = source.get_data(args.artist)
    print (ret)

