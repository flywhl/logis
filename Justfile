default:
    @just --list

test:
    @uv run pytest

test-s:
    @uv run pytest -s -o log_cli=True -o log_cli_level=DEBUG

fix:
    uv run ruff format .
    uv run ruff check --fix

lint:
    uv run ruff check logis
    uv run pyright logis

lint-file file:
    - ruff {{file}}
    - pyright {{file}}
