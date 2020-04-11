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

    asyncio.run(create_superuser(app.state.db, username, password))


async def create_superuser(db: Database, username: str, password: str):
    admin = UserModel(
        uid=uuid4(),
        username=username,
        disabled=False,
        created=arrow.utcnow().datetime,
        is_admin=True,
    )
    query = orm.User.insert().values(admin.dict(), hashed_password=crypt_context.hash(password))
    async with db:
        async with db.transaction():
            await db.execute(query)

    click.echo(f"created admin with username {username!r}, uuid {str(admin.uid)!r}.")


if __name__ == "__main__":
    cyberbox()
