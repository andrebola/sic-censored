from flask import Flask
from flask import render_template
from whitenoise import WhiteNoise

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

@app.route("/")
def index():
	return render_template("map.html")


if __name__ == '__main__':
    app.run(debug=True)
