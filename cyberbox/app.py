import os

from flask import Flask
from sqlalchemy import create_engine

from .models import init_app, Session, User, init_db


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
        session = Session()
        session.add(User(username="123"))
        print([f"{user.uuid} {type(user.uuid)}" for user in User.query.all()])
        return "Hello world!"

    engine = create_engine(
        "postgresql+psycopg2://devuser:devpass@localhost:5432/cyberbox-db"
    )
    init_db(engine)
    Session.configure(bind=engine)
    init_app(app)

    return app
