import math
from typing import Type

from databases import Database
from sqlalchemy import Table, asc, func, select

from cyberbox.models import FilterParams


async def pagination(
    select_query, db_model: Table, page_model: Type, db: Database, params: FilterParams
):
    """ Paginates query and constructs page model.

    :param select_query: query to be paginated.
    :param db_model: table object is required to construct sort by "created" field.
    :param page_model: class used to construct page instance.
    :param db: to execute database queries.
    :param params: filter params from API.
    :return: page instance.
    """
    page, limit, offset = params.page, params.limit, params.offset()

    items_query = select_query.limit(limit).offset(offset).order_by(asc(db_model.c.created))
    items = await db.fetch_all(items_query)

    count_query = select([func.count()]).select_from(select_query.alias())
    total_count = await db.execute(count_query)

    has_previous = page > 1
    previous_page_number = page - 1 if has_previous else None

    has_next = (offset + len(items)) < total_count
    next_page_number = page + 1 if has_next else None

    return page_model(
        items=items,
        total=total_count,
        pages=int(math.ceil(float(total_count) / float(limit))),
        has_next=has_next,
        has_previous=has_previous,
        next_page_number=next_page_number,
        previous_page_number=previous_page_number,
    )
