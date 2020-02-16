import os

from flask import Flask


def create_app(testing_config: dict = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")

    if testing_config is None:
        app.config.from_pyfile("config.py", True)
    else:
        app.config.from_mapping(testing_config)

    os.makedirs(app.instance_path, exist_ok=True)

    @app.route("/")
    def hello():
        return "Hello world!"

    return app
