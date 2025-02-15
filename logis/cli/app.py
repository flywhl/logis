import click

from dishka.integrations.click import setup_dishka

from logis.cli.commands.query import query
from logis.util.di import DI


def start():
    @click.group()
    @click.pass_context
    def main(context: click.Context):
        di = DI()
        setup_dishka(container=di.container, context=context, auto_inject=True)

    main.command("query")(query)

    main()
