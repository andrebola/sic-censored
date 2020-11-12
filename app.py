import json
from flask import Flask, escape, request, render_template, make_response
from whitenoise import WhiteNoise
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
import glob
import unicodedata

nav = Nav()
# registers the "top" menubar
nav.register_element(
    'top',
    Navbar(
        View('Forbidden Territories', 'index'),
        View('Map', 'map'),
        View('Data', 'data_main'),
        View('About', 'about'),
        Link('github', 'https://github.com/andrebola/sic-censored'), 
    )
)

app = Flask(__name__)
Bootstrap(app)
nav.init_app(app)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/map")
def map():
    data = json.load(open(f'map/custom_light.geo.json'))
    return(render_template("map.html", data = data))

@app.route('/data/')
def data_main():
    return data("spain")

def clean_words(words, clean=True):
    if clean:
        for word in words.split():
            for i, c in enumerate(word):
                if not unicodedata.name(c).startswith("LATIN"):
                    word  = word[:i].lower()
                else: 
                    word = word.lower()
        return "".join(words).replace('\n', ' ').replace('\r', '')
    else: return words.replace('\n', ' ').replace('\r', '')

@app.route("/data/<country>")
def data(country):
    data = json.load(open('data/{}.json'.format(escape(country.replace(".", "")))))
    lyrics_artists = json.load(open(str(glob.glob(f'scrapers/songlyrics/*{country}.json')[0])))
    lyrics = ''
    for artist in lyrics_artists:
        if len(artist['lyrics']):
            for l in artist['lyrics']:
                lyrics += " "+l
            #lyrics += " "+artist['lyrics'][0]
    lyrics = clean_words(lyrics, clean=False)

    return(render_template("data.html", data = data, lyrics = lyrics))

@app.route('/<page_name>')
def other_page(page_name):
    response = make_response(render_template('404.html'), 404)
    return response


if __name__ == '__main__':
    app.run(debug=True)
