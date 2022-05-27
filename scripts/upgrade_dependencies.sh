#!/bin/bash
set -euxo pipefail

# Move to the project's root folder since the python script expects to be run here.
scripts_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
root_path=$( cd "$(dirname "$scripts_path")" ; pwd -P )
cd "$root_path"

poetry run python scripts/python_scripts/upgrade_dependencies.py
