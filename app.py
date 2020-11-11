import json
from flask import Flask
from flask import render_template, make_response
from whitenoise import WhiteNoise
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *

nav = Nav()
# registers the "top" menubar
nav.register_element(
    'top',
    Navbar(
        View('Forbidden Territories', 'index'),
        View('Map', 'map'),
        View('Data', 'data'),
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
@app.route("/data/<country>")
def data(country="spain"):
    data = json.load(open(f'data/{country}.json'))
    return(render_template("data.html", **data))

@app.route('/<page_name>')
def other_page(page_name):
    response = make_response(render_template('404.html'), 404)
    return response


if __name__ == '__main__':
    app.run(debug=True)
