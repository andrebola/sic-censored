import urllib
import lxml.html
from urllib.request import urlopen, Request
import json
import pprint
import time
import argparse

class Musixmatch(object):

    def _search(self, artist, title=None):
        if title != None:
            search = urllib.parse.quote_plus("%s %s" % (artist, title))
        else:
            search = urllib.parse.quote_plus(artist.encode('utf-8'))
        url = 'https://www.musixmatch.com/search/%s/tracks' % search
        #print (url)
        req = Request(url, headers={'User-Agent' : "Magic Browser"})
        u = urlopen(req)
 
        page = lxml.html.parse(u)
        links = page.getroot().cssselect('.showArtist')
        ret = []
        for i in links:
            inner_content = i.cssselect('.has-secondary-actions')
            if not len(inner_content):
                links = i.cssselect('.title')
                ret.append(links[0].get('href'))
        return ret

    def get_data(self, artist, title=None):
        urls = self._search(artist, title)
        print ("Found {} tracks, start collecting each track...".format(len(urls)))
        ret = []
        for url in urls:
            try:
                time.sleep(1)
                lyric = self._get_lyrics_from_url(url)
                #pprint.pprint (lyric)
                extra_data = ""
                if 'track' in lyric['page']:
                    extra_data = lyric['page']['track']
                lyric_content = lyric['page']['lyrics']['lyrics']['body']
                ret.append((extra_data, [lyric_content]))
                print ("Collected lyric ", url)
            except Exception as e:
                print (e, url)
        return ret

    def _get_lyrics_from_url(self, url):
        url = 'https://www.musixmatch.com/' + url
        #print (url)
        req = Request(url, headers={'User-Agent' : "Magic Browser"})
        u = urlopen(req)
        page = lxml.html.parse(u)
        for s in page.getroot().cssselect('script'):
            c = s.text_content()
            if '__mxmState' in c:
                content = c.split('var __mxmState = ')
                return json.loads(content[1][:-1])
        return {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download lyrics.')
    parser.add_argument('--artist', dest='artist')
    args = parser.parse_args()
    source = Musixmatch()
    ret = source.get_data(args.artist)
    print (ret)
