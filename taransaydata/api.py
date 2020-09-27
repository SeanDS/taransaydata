"""Taransay data service REST API"""

from flask import Flask, redirect, send_from_directory
from flask_cors import CORS
from .apiv1 import app as apiv1

app = Flask(__name__)
CORS(app)
app.register_blueprint(apiv1, url_prefix="/v1")


@app.route("/")
def api():
    return redirect("/v1")


@app.route("/chart")
def chart():
    return send_from_directory(".", "plot.html")
