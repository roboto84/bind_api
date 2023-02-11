# syntax=docker/dockerfile:1
FROM python:3.10-slim
WORKDIR /usr/src/roboto_api

# Update apt-get
RUN apt-get update -y

# Install libenchant
RUN apt-get install -y libenchant-2-2

# Install poetry
ENV POETRY_VERSION=1.2.0
RUN apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | POETRY_VERSION=${POETRY_VERSION} python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install project dependencies via poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install

# Set environmental variables for application
ENV HOST_SERVER_ADDRESS=127.0.0.1 \
    SOCKET_SERVER_PORT=3001 \
    HTTP_SERVER_PORT=8000

# Copy application
COPY . .

# Run application
EXPOSE 8000
CMD ["poetry", "run", "python", "roboto_api/roboto_api.py"]
