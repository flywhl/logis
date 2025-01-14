default:
    @just --list

test:
    @uv run pytest

test-s:
    @uv run pytest -s -o log_cli=True -o log_cli_level=DEBUG

ruff-fix:
    uv run ruff format mthd

ruff-check:
    uv run ruff check mthd

pyright:
    uv run pyright mthd

lint:
    just ruff-check
    just pyright

lint-file file:
    - ruff {{file}}
    - pyright {{file}}
