# from multiprocessing import Process
import os
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from gpy.config import import_config


def disable_https():
    """Allow insecure HTTP (non-HTTPS) calls."""
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def set_up_flask_server():
    """Create and register Flask server blueprint."""
    cfg = import_config()['legacy']
    app = Flask(__name__)
    app.secret_key = "supersekrit"
    blueprint = make_google_blueprint(
        client_id=cfg['client_id'],
        client_secret=cfg['client_secret'],
        scope=[
            'https://www.googleapis.com/auth/plus.me',
            'https://www.googleapis.com/auth/userinfo.email',
        ]
    )
    app.register_blueprint(blueprint, url_prefix='/login')

    @app.route('/')
    def index():
        """Respond to the root view ('/')."""
        if not google.authorized:
            return redirect(url_for('google.login'))
        resp = google.get('/oauth2/v2/userinfo')
        assert resp.ok, resp.text
        return f"You are {resp.json()['email']} on Google bleh!"

    return app


def get_token():
    """Run OAuth app."""
    disable_https()
    app = set_up_flask_server()
    app.run()
