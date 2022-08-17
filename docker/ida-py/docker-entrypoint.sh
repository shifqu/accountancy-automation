#!/bin/sh

set -e

# Activate the virtual environment
# shellcheck source=/dev/null
. "$VENV_PATH/.venv/bin/activate"

# Evaluate passed command
exec "$@"
