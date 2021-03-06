import json
from flask import Flask, escape, request, render_template, make_response, jsonify, make_response
from whitenoise import WhiteNoise
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
import glob
import ftfy
import os
import unicodedata
from collections import defaultdict
from collections import Counter
from random import choice, choices
import re

nav = Nav()
# registers the "top" menubar
nav.register_element(
    'top',
    Navbar(
        View('Forbidden Territories', 'index'),
        View('Map', 'map'),
        View('Data', 'data_main'),
        View('Query', 'lyric_query'),
        View('Team', 'about'),
        View('Manifesto', 'manifesto'),
        Link('github', 'https://github.com/andrebola/sic-censored'), 
    )
)

app = Flask(__name__)
Bootstrap(app)
nav.init_app(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/manifesto")
def manifesto():
	return render_template("manifesto.html")


@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/query")
def lyric_query():
	return render_template("query.html")


@app.route("/map")
def map():
    data = json.load(open(f'map/custom_light.geo.json'))
    return(render_template("map.html", data = data))

@app.route('/data/')
def data_main():
    return data("spain")

def clean_words(words, clean=True):
    if clean:
        cwords = []
        for word in words.split():
            cword = ''
            for c in word:
                try:
                    cword += re.sub('\W+','', ftfy.ftfy(c) )
                except: pass
            cwords.append(cword)
        return " ".join(cwords)
    else: return words.replace('\n', ' ').replace('\r', '')

    
@app.route("/ajax/data/<country>")
def dict_lyrics(country):   
    data = json.load(open('data/{}.json'.format(escape(country.replace(".", "")))))
    lyrics_artists = json.load(open(str(glob.glob(f'scrapers/songlyrics/*{country}*.json')[0]), encoding='utf-8'))
    
    stop_words = set(json.load(open("data/en_stopwords.json")))
    if country in ['spain', 'argentina', 'dominican-rep','chile','peru']:
        stop_words.update(set(json.load(open("data/es_stopwords.json"))))
    elif country in ['france']:
        stop_words.update(set(json.load(open("data/fr_stopwords.json"))))
    elif country in ['brazil', 'portugal']:
        stop_words.update(set(json.load(open("data/pt_stopwords.json"))))
    elif country in ['italy']:
        stop_words.update(set(json.load(open("data/it_stopwords.json"))))
    
    print (country)
    lyrics = defaultdict(int)
    for artist in lyrics_artists:
        if len(artist['lyrics']):
            for l in artist['lyrics']:
                for w in l.split():
                    clean_w = re.sub('\W+','', ftfy.ftfy(w) ).replace('\n', '').replace('\r', '')
                    if clean_w.lower() not in stop_words and not clean_w.isnumeric() and clean_w!='':
                        lyrics[clean_w.lower()] += 1
    return make_response(jsonify(lyrics))

def blocks(text, n):
    p = text + text[:n - 1]
    p = dict(Counter([p[i:i + n] for i in range(len(text))]))
    p = [[p[x], x] for x in p]
    p.sort()
    return p

def generate(text, maxlen, n):
    if n == 1:
        t = ''
        for i in range(maxlen): t += text[choice(range(len(text)))]
        return t
    p = blocks(text, n)
    t = choices([x[1] for x in p], [x[0] for x in p])[0]
    while len(t) < maxlen:
        f = t[-n + 1:]
        pp = [x for x in p if x[1][:n - 1] == f] 
        t = t + choices([x[1] for x in pp], [x[0] for x in pp])[0][-1]
    return t

@app.route("/ajax/data/<country>/create")
def create_lyrics(country):
    lyrics_artists = json.load(open(str(glob.glob(f'scrapers/songlyrics/*{country}*.json')[0]), encoding='utf-8'))
    lyrics = []
    for artist in lyrics_artists:
        if len(artist['lyrics']):
            for l in artist['lyrics']:
                for w in l.split():
                    clean_w = re.sub('\W+','', ftfy.ftfy(w) ).replace('\n', ' \n').replace('\r', '\r')
                    lyrics.append(clean_w)
    return make_response(generate(" ".join(lyrics), maxlen = 500, n = 6))

@app.route("/data/<country>")
def data(country):
    country_file = 'data/{}.json'.format(escape(country.replace(".", "")))
    if os.path.isfile(country_file): 
        data = json.load(open(country_file))
        return(render_template("data.html", country=country, data = data))
    return render_template('404.html', title = '404'), 404

@app.route('/<page_name>')
def other_page(page_name):
    response = make_response(render_template('404.html'), 404)
    return response

def select_country(text):
    match = re.search(r"(?<=\/\s).*$", text)
    return match.group()

if __name__ == '__main__':
    app.jinja_env.filters['select_country'] = select_country
    app.run(debug=True, port=5000)
