from uuid import uuid4

import click
from flask import Flask, current_app
from flask.cli import with_appcontext
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import UUIDType, force_auto_coercion

force_auto_coercion()

Session = scoped_session(sessionmaker())

Base = declarative_base()
Base.query = Session.query_property()


def init_db(app: Flask = current_app):
    engine = create_engine("postgresql+psycopg2://devuser:devpass@localhost:5432/cyberbox-db")
    Session.configure(bind=engine)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_cmd)


@click.command("init-db")
@with_appcontext
def init_db_cmd():
    init_db()
    click.echo("Initialized the database.")


def close_db(exc=None):
    if exc is None:
        Session().commit()
    else:
        Session().invalidate()

    Session.remove()


class User(Base):
    __tablename__ = "user"

    uuid = Column(UUIDType(), default=uuid4, primary_key=True)
    # username = Column(String(), unique=True, nullable=False)
    username = Column(String(), nullable=False)
