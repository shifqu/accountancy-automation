FROM python:3.10.6-bullseye as base

# Set working directory
ENV PROJECT_ROOT="/opt/ida-py"
WORKDIR $PROJECT_ROOT

# Add the app-user
RUN adduser --disabled-password --gecos "" idauser

# Set python related environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=0

# Set poetry environment variables
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV VENV_PATH="/opt/pyvenv"

# Set path to include POETRY_HOME
ENV PATH="$POETRY_HOME/bin/:$VENV_PATH/bin:$PATH"

### Build stage
FROM base as build

# Install build dependencies
RUN apt-get update && \
    apt-get install --yes curl && \
    rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Install dependencies
WORKDIR $VENV_PATH
COPY ./poetry.loc[k] ./pyproject.toml .
RUN poetry install --no-dev

### Development stage
FROM base as development

# Set the env to DEVELOPMENT
ENV API_ENV=DEVELOPMENT

# Install system dependencies
RUN apt-get update && \
    apt-get install --yes curl cron git vim && \
    rm -rf /var/lib/apt/lists/*

# Copy poetry
COPY --from=build --chown=idauser $POETRY_HOME $POETRY_HOME

# Copy the virtual environment
COPY --from=build --chown=idauser $VENV_PATH $VENV_PATH

# Copy the entrypoint and make it executable
COPY ./docker/ida-py/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Change to app-user
USER idauser

# Install dev dependencies
WORKDIR $VENV_PATH
RUN poetry install

# Copy the source of the project
WORKDIR $PROJECT_ROOT
COPY ./ida_py ./ida_py
COPY ./poetry.loc[k] ./pyproject.toml README.md .

# Install the project inside the $VENV_PATH
RUN . "$VENV_PATH/.venv/bin/activate" && \
    poetry install

# Copy all files for development purposes
COPY . .

# Specify the entrypoint in exec form (cfr: https://docs.docker.com/engine/reference/builder/#entrypoint)
ENTRYPOINT ["/docker-entrypoint.sh"]

# Serve the api
CMD ["python", "ida_py/api/main.py"]

### PRODUCTION stage (untested)
FROM base as production

# Set the env to PRODUCTION
ENV API_ENV=PRODUCTION

# Copy poetry (to be removed in a later stage)
COPY --from=build --chown=idauser $POETRY_HOME $POETRY_HOME

# Copy the virtual environment
COPY --from=build --chown=idauser $VENV_PATH $VENV_PATH

# Copy the source of the project
WORKDIR $PROJECT_ROOT
COPY ./ida_py ./ida_py
COPY ./poetry.loc[k] ./pyproject.toml README.md .

# Install the project inside the $VENV_PATH and remove $POETRY_HOME
RUN . "$VENV_PATH/.venv/bin/activate" && \
    poetry install --no-dev && \
    rm -rf "$POETRY_HOME"

# Copy the entrypoint and make it executable
COPY ./docker/ida-py/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Make idauser owner of all files
RUN chown -R idauser.idauser .

# Change to app-user
USER idauser

# Specify the entrypoint in exec form (cfr: https://docs.docker.com/engine/reference/builder/#entrypoint)
ENTRYPOINT ["/docker-entrypoint.sh"]

# Serve the api (TODO: Use gunicorn)
CMD ["python", "ida_py/api/main.py"]
