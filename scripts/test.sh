#!/bin/bash
set -euxo pipefail

poetry run pytest -s --cov=ida_py/ --cov=tests --cov-report=term-missing "${@-}" --cov-report html
