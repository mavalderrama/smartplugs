import os

from flask import Flask
from flask_restful import Api

# db variable initialization
api = Api()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.urandom(42)

    with app.app_context():
        # Imports
        from . import server

        api.init_app(app)
        return app
