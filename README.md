# ida-py
IDA (I Do Accountancy). A python project to automate tedious accountancy tasks.

---

<!-- [![PyPI version](https://badge.fury.io/py/ida-py.svg)](http://badge.fury.io/py/ida-py) -->
<!-- [![codecov](https://codecov.io/gh/shifqu/ida-py/branch/master/graph/badge.svg)](https://codecov.io/gh/shifqu/ida-py) -->
<!-- [![Downloads](https://pepy.tech/badge/ida-py)](https://pepy.tech/project/ida-py) -->
[![Test Status](https://github.com/shifqu/ida-py/actions/workflows/test.yml/badge.svg)](https://github.com/shifqu/ida-py/actions?query=workflow%3ATest)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/ida-py/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat)](https://pycqa.github.io/isort/)

---
## System requirements
ida-py requires [Python 3.10+](https://www.python.org/downloads/) and [Poetry 1.0+](https://python-poetry.org/docs/).

##### Tip: The recommended IDE is [VSCode](https://code.visualstudio.com/). A `.vscode` directory is provided with a file containing recommended extensions alongside default launch configurations and workspace specific settings.
## Installation
ida-py uses Poetry to manage the virtual environments. This makes installing the application locally a breeze.  
```bash
poetry install

poetry run pip install --upgrade pip

poetry update

poetry run pre-commit install -t pre-commit -t pre-push
```
##### Tip: This repository ships with a bash script (./scripts/install.sh) which will run above commands for you.

## Configuration
To [enable telegram webhooks](https://core.telegram.org/bots/webhooks), we need a certificate and a domain name.
### Domain name
Obtaining a domain name will not be covered here, since it's covered by [telegram's webhook guide](https://core.telegram.org/bots/webhooks).

certbot and nginx are used in this project to generate certificates and serve the content over https.

##### Note: To counter a cold-start issue where the certificates are not found, a script (docker/nginx/wait_for_certificates.sh) is used to wait for the initial creation of the certificates.

##### Tip: In case things don't work with certificate generation, add `--test-cert` to `certbot` service's `command` to avoid letsencrypt's 5 failed attempts hourly rate limit.

## Environment variables
To configure IDA, a few environment variables are mandatory, whilst others are optional.
Mandatory environment variables are checked by docker-compose or at runtime. Simply adding the 
environment variables to a `.env` file will ensure that docker-compose injects the variables at 
runtime.

Run the services in development mode:
```bash
docker compose up -d --build
```
Run the services in production mode
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```
At some point you will have to renew the certificates. Currently this is not supported automatically.
```bash
docker compose up certbot && docker compose exec -it nginx nginx -s reload
```

---
[Read Latest Documentation](https://shifqu.github.io/ida-py/) - [Browse GitHub Code Repository](https://github.com/shifqu/ida-py/)

---
