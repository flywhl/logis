import click

from dishka import FromDishka

from mthd.service.query import QueryService


@click.argument("query", type=str)
@click.option("limit", "--limit", type=int, default=-1)
def query(query: str, limit: int, query_service: FromDishka[QueryService]):
    query_parts = query.split(" ")
    print(query_parts)
    if len(query_parts) != 3:
        raise ValueError(f"Invalid query: {query}")

    result = query_service.execute_simple(*query_parts, limit=limit)

    print(result)
