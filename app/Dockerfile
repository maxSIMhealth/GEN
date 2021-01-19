# Official python image
FROM python:3.8-alpine

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# User and group ids
ARG USER_ID
ARG GROUP_ID

# Create user that will run the project
RUN addgroup -S gen --gid $GROUP_ID \
    && adduser -S -G gen -h /opt/gen --uid $USER_ID -D gen 

# Set app home directory
ENV APP_HOME=/opt/gen

# Create and set working directory for the project files
WORKDIR $APP_HOME

# Create django's static and media directories
RUN mkdir -p $APP_HOME/static
RUN mkdir -p $APP_HOME/media

# Copy project requirements file
COPY ./requirements.txt requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Install necessary system packages
RUN apk add --update --no-cache postgresql-client postgresql-contrib ffmpeg libmagic gettext

# Install packages needed only during install phase
RUN apk add --update --no-cache --virtual .temp-build-deps \
    gcc make linux-headers libc-dev zlib-dev jpeg-dev \
    python3-dev postgresql-dev

# Install python packages
RUN pip install -r requirements.txt --no-cache-dir

# Remove packages needed only during install phase
RUN apk del .temp-build-deps

# Change to the directory containing manage.py for running Django commands
WORKDIR $APP_HOME/app

# Copy project files
#COPY . $APP_HOME

# Set user as project directory owner
RUN chown -R gen:gen $APP_HOME

# Activate user
USER gen

