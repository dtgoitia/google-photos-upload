import os
import sys
from flask import Flask, redirect, url_for, request
from flask_dance.contrib.google import make_google_blueprint, google
from gpy.config import import_config


def enable_flask_debug_mode():
    """Enable Flask debug mode."""
    os.environ['FLASK_DEBUG'] = '1'


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
        global access_token
        access_token = google.token
        # print(f'TOKEN = {access_token}', file=sys.stderr)
        resp = google.get('/oauth2/v2/userinfo')
        assert resp.ok, resp.text
        content = f"""
        <div>You are {resp.json()['email']} on Google bleh!</div>
        <a href="http://localhost:5000/shutdown">CLICK HERE TO CLOSE</a>
        """
        return content

    @app.route('/shutdown')
    def shutdown():
        """Shutdown Flask server."""
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'Server shutting down...'

    @app.route('/albums')
    def albums():  # noqa
        resp = google.get('/oauth2/v2/userinfo')
        print(resp)
        return f'{resp.text}'

    return app


def get_token():
    """Run OAuth app."""
    access_token = ''
    # enable_flask_debug_mode()
    disable_https()
    app = set_up_flask_server()
    app.run()
    print(google.token, file=sys.stderr)
    print(f'\n\ntoken = {access_token}', file=sys.stderr)
    return 'success!'
