from threading import Thread as thread
from collections import defaultdict
from repl_likes import getlikers
from time import sleep as wait
from os import environ as env
from ratelimit import limits
from random import choice
from requests import get
from io import BytesIO
from PIL import Image
import collections
import base64
import flask
import os


def rgbtohex(rgb): return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


app = flask.Flask(__name__)


@app.route("/")
def main(): return flask.render_template("index.html")


@app.route("/api", methods=["POST"])
@limits(calls=10, period=5)
def api():
    try:
        data = BytesIO(base64.b64decode("".join(flask.request.get_json(force=True)["base64"].split(",")[1:])))
        image = Image.open(data)
        id = "".join([choice("1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM") for i in range(10)])
        image.save(f"{id}.png")
        size = os.stat(f"{id}.png").st_size
        os.remove(f"{id}.png")
        max = 5e+6

        if "X-Replit-User-Name" in flask.request.headers:
            if flask.request.headers["X-Replit-User-Name"] in getlikers(
                "/@hyperhacker/Image-Colour-Palette-Generator"): max = 10e+6

        if size < max:
            bc = defaultdict(int)
            for i in image.getdata(): bc[i] += 1
            new = {rgbtohex(k): v for k, v in bc.items()}

            return {"vals": new}
        return {"error": "File too large"}
    except:
        return {"error": "An error occurred"}


def keepalive():
    while True:
        get(f"https://{env['REPL_SLUG']}.{env['REPL_OWNER']}.repl.co")
        wait(60)


thread(target=keepalive, daemon=True).start()

app.run("0.0.0.0")
