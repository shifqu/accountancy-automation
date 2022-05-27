#!/bin/bash
set -euo pipefail

if poetry install; then
    echo 'successfully installed poetry env'
    if poetry run pip install --upgrade pip; then
        echo 'successfully updated pip'
        if poetry update; then
            echo 'successfully updated dependencies'
        else
            echo 'fatal: could not update dependencies'
        fi
    else
        echo 'fatal: coulld not upgrade pip'
    fi
    if poetry run pre-commit install -t pre-commit -t pre-push -t commit-msg; then
        echo 'successfully installed pre-commit hooks'
        echo 'use "poetry shell" to activate the new virtual environment'
        echo 'more info: https://python-poetry.org/docs/basic-usage/#activating-the-virtual-environment'
    else
        echo 'fatal: could not install pre-commit'
    fi
else
    echo 'fatal: "poetry install" failed'
fi
