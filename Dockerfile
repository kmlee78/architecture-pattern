FROM python:3.10-slim as base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential
ENV PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=$PYTHONPATH:. \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME=$HOME/.poetry \
    POETRY_VERSION=1.3.2 \
    WORKDIR=/workspace
ENV PATH="$POETRY_HOME/bin:$PATH"
WORKDIR $WORKDIR
EXPOSE 8000

FROM base as poetry_installer
RUN curl -sSL https://install.python-poetry.org | python3 -

FROM base as dev
COPY --from=poetry_installer $POETRY_HOME $POETRY_HOME

FROM base as package_installer
COPY --from=poetry_installer $POETRY_HOME $POETRY_HOME
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --without dev

FROM base as prod
COPY --from=package_installer /usr/local/bin /usr/local/bin
COPY --from=package_installer /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY ./app ./app
CMD uvicorn app.main:app --reload 