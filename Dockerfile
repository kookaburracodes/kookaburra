FROM python:3.11.0-slim

# Set workdir
WORKDIR /app

# Copy dependencies
RUN mkdir -p /app/kookaburra
COPY pyproject.toml /app
COPY kookaburra/__init__.py /app/kookaburra

# Install dependencies
RUN apt-get update -y \
    && apt-get install git -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --no-cache-dir . \
    && rm -rf $(pip cache dir)

# Copy source code
COPY . /app

# Run
CMD gunicorn kookaburra.main:app -c kookaburra/gunicorn_conf.py
