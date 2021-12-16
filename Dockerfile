FROM python:3.10-slim as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
#RUN apt-get update && apt-get install -y --no-install-recommends gcc
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    gcc && \
    apt-get -qq clean && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies in /.venv
COPY Pipfile Pipfile.lock /
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy


FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN useradd --home-dir /app --create-home --skel=/dev/null --no-log-init app
WORKDIR /app
USER app

ARG BUILD_DATE
ARG BUILD_VERSION=0.0.0
ARG VCS_REF

ENV BUILD_DATE=$BUILD_DATE \
    BUILD_VERSION=$BUILD_VERSION \
    LISTEN_PORT=8000 \
    LOG_LEVEL=warning \
    VCS_REF=$VCS_REF

# Install application into container
COPY src/ .

# Run the application
ENTRYPOINT ["/app/fundraiser.py"]
#CMD ["--directory", "directory", "8000"]
#CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"


#FROM python:3.10-slim-bullseye
#
#ENV TZ=Europe/Amsterdam
#
#RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
#    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
#    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
#    pipenv && \
#    apt-get -qq clean && \
#    rm -rf /var/lib/apt/lists/*
#
#WORKDIR /app
#ADD Pipfile Pipfile.lock /app/
#RUN pipenv install

#CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
