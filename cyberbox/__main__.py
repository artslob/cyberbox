import asyncio
from uuid import uuid4

import arrow
import click
from databases import Database

from cyberbox import orm
from cyberbox.models import UserModel
from cyberbox.routes.auth import crypt_context


@click.group()
def cyberbox():
    pass


@cyberbox.command()
@click.option("--username", required=True)
@click.password_option(required=True)
def create_admin(username: str, password: str):
    """ Creates superuser with given username and password. """
    from cyberbox.asgi import app

    admin = asyncio.run(_create_admin(app.state.db, username, password))
    click.echo(f"created admin with username {username!r}, uuid {str(admin.uid)!r}.")


async def _create_admin(db: Database, username: str, password: str) -> UserModel:
    # split on separate funcs for testing
    async with db as db:
        async with db.transaction():
            return await __create_admin(db, username, password)


async def __create_admin(db: Database, username: str, password: str) -> UserModel:
    admin = UserModel(
        uid=uuid4(),
        username=username,
        disabled=False,
        created=arrow.utcnow().datetime,
        is_admin=True,
    )

    query = orm.User.insert().values(admin.dict(), hashed_password=crypt_context.hash(password))
    await db.execute(query)

    return admin


if __name__ == "__main__":
    cyberbox()
