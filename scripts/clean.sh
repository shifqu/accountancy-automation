#!/bin/bash
set -euxo pipefail

poetry run isort ida_py/ tests/
poetry run black ida_py/ tests/
