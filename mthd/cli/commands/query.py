import click

from dishka import FromDishka

from mthd.service.query import QueryService


@click.argument("query", type=str)
@click.option("limit", "--limit", type=int, default=-1)
def query(query: str, limit: int, query_service: FromDishka[QueryService]):
    query_parts = query.split(" ")
    if len(query_parts) != 3:
        raise ValueError(f"Invalid query: {query}")

    result = query_service.execute_simple(*query_parts, limit=limit)

    if result.is_empty:
        click.echo("No results found.")
        return

    click.echo(f"Found {len(result.commits)} commit(s):")
    for commit in result.commits:
        click.echo(f"\t{commit.sha:7} {commit.to_semantic().summary}")
        click.echo("\n")
