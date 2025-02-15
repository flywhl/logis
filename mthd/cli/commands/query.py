import sys

import click

from dishka import FromDishka
from rich.console import Console

from mthd.service.query import QueryService


@click.argument("query", type=str)
@click.option("limit", "--limit", type=int, default=-1)
@click.option("full_sha", "--full-sha", is_flag=True, type=bool, default=False)
def query(query: str, limit: int, full_sha: bool, query_service: FromDishka[QueryService]):
    console = Console()
    query_parts = query.split(" ")
    if len(query_parts) != 3:
        console.print(f"[b]Invalid query:[/b] {query}")
        sys.exit(1)

    result = query_service.execute_simple(*query_parts, limit=limit)

    if result.is_empty:
        console.print("[b]No results found.[/b]")
        return

    console.print(f"Found {len(result.commits)} commit(s):\n")
    for commit in result.commits:
        sha = commit.sha if full_sha else commit.sha[:7]
        sha_len = 40 if full_sha else 7
        console.print(f"\t[b]{sha:<{sha_len + 3}}[/b]{commit.to_semantic().summary}")
