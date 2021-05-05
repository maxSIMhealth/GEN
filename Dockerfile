# Official python image
FROM python:3.8.10-alpine3.13

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Copy project requirements file
COPY app/requirements.txt /app/requirements.txt

## Install packages, create virtualenv, and install dependencies
# Upgrade pip
RUN pip install --upgrade pip

# Install necessary system packages
RUN apk add --update --no-cache postgresql-client postgresql-contrib ffmpeg libmagic gettext

# Install packages needed only during install phase
RUN apk add --update --no-cache --virtual .temp-build-deps \
    gcc make linux-headers libc-dev zlib-dev jpeg-dev \
    python3-dev postgresql-dev

# Install python packages
RUN pip install -r /app/requirements.txt --no-cache-dir

# Remove packages needed only during install phase
RUN apk del .temp-build-deps

# Copy project
ADD app /app

# Change to the directory containing manage.py for running Django commands
WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "GEN.asgi:application", "--bind", ":8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]
