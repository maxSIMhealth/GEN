# Official python image
FROM python:3.8-alpine

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Create and set working directory for the project files
RUN mkdir -p /opt/gen/src
WORKDIR /opt/gen/src

# Copy project requirements file
COPY ./requirements.txt requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Install necessary system packages
RUN apk add --update --no-cache postgresql-client postgresql-contrib ffmpeg libmagic

# Install packages needed only during install phase
RUN apk add --update --no-cache --virtual .temp-build-deps \
    gcc make linux-headers libc-dev zlib-dev jpeg-dev \
    python3-dev postgresql-dev

# Install python packages
RUN pip install -r requirements.txt --no-cache-dir

# Remove packages needed only during install phase
RUN apk del .temp-build-deps

# Copy project files
COPY . .

# Create and activate user that will run the project
RUN addgroup -S gen \
    && adduser -S -G gen -h /home/gen -D gen
USER gen

RUN mkdir -p /home/gen/static
RUN mkdir -p /home/gen/media

# Change to the directory containing manage.py for running Django commands
WORKDIR /opt/gen/src/app
