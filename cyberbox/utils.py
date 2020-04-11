from enum import Enum

from databases import Database
from sqlalchemy import func, select


class AutoName(Enum):
    """ Base class for enums with equal string names and values. """

    def _generate_next_value_(name, start, count, last_values):
        return name


async def exec_count(db: Database, from_):
    query = select([func.count()]).select_from(from_)
    return await db.execute(query)
