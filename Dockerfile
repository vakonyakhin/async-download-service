# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9.23-slim-bookworm

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN apt-get update && apt-get upgrade -y && apt-get install -y zip


WORKDIR /app
COPY . /app

ENV STORAGE_DIR=./test_photos/
ENV DELAY=1
ENV LOG_LEVEL=INFO
ENV CHUNK_SIZE=300000


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
ENTRYPOINT ["python", "server.py"]

