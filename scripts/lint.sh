#!/bin/bash
set -euxo pipefail

poetry run cruft check
find scripts/ -type f -not -name '*py' | poetry run xargs shellcheck
poetry run isort --check --diff ida_py/ tests/
poetry run black --check ida_py/ tests/
poetry run pydocstyle ida_py/ tests/
poetry run flake8 ida_py/ tests/
poetry run mypy ida_py/
poetry run bandit -r ida_py/
poetry run safety check
