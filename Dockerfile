# Use official Python base image
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# System deps
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && apt-get clean \

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

COPY pyproject.toml ./

# Copy the application code into the container
COPY sample_postgres.py ./

RUN uv sync

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the Flask app using Gunicorn when the container launches
# This is a production-ready WSGI server
# It now points to the 'app' object inside your 'sample_postgres.py' file
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "sample_postgres:app"]
