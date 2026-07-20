import os
import re

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

OSCAR_API = os.environ.get("OSCAR_API_URL", "http://open-oscar-server:8080")
OSCAR_HOST = os.environ.get("OSCAR_HOST", "aim.example.com")
OSCAR_PORT = os.environ.get("OSCAR_PORT", "5190")
NETWORK_NAME = os.environ.get("NETWORK_NAME", "AIM Network")
SCREEN_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 ]{2,15}$")


@app.context_processor
def inject_branding():
    return {
        "oscar_host": OSCAR_HOST,
        "oscar_port": OSCAR_PORT,
        "network_name": NETWORK_NAME,
    }


def normalize(screen_name: str) -> str:
    return screen_name.replace(" ", "").lower()


def screen_name_taken(screen_name: str) -> bool:
    resp = requests.get(f"{OSCAR_API}/user", timeout=5)
    resp.raise_for_status()
    target = normalize(screen_name)
    return any(normalize(u["screen_name"]) == target for u in resp.json())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["POST"])
def signup():
    screen_name = request.form.get("screen_name", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    if not SCREEN_NAME_RE.match(screen_name):
        return render_template(
            "error.html",
            message="Screen names must be 3-16 characters, start with a letter, "
                    "and use only letters, numbers, and spaces.",
        )
    if len(password) < 4 or len(password) > 32:
        return render_template(
            "error.html", message="Passwords must be between 4 and 32 characters."
        )
    if password != confirm:
        return render_template("error.html", message="Your passwords didn't match. Try again!")

    try:
        if screen_name_taken(screen_name):
            return render_template(
                "error.html",
                message=f'Sorry, "{screen_name}" is already taken. Try another screen name!',
            )
        resp = requests.post(
            f"{OSCAR_API}/user",
            json={"screen_name": screen_name, "password": password},
            timeout=5,
        )
        if not resp.ok:
            return render_template(
                "error.html",
                message="The server rejected that screen name. Try a different one!",
            )
    except requests.RequestException:
        return render_template(
            "error.html",
            message="Our server's taking a coffee break. Please try again in a moment.",
        )

    return render_template("success.html", screen_name=screen_name)


@app.route("/guide")
def guide():
    return render_template("guide.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
