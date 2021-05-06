# Official python image
FROM python:3.8.10-alpine3.13

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Copy project requirements file
COPY app/requirements.txt /app/requirements.txt

## Install packages, create virtualenv, and install dependencies
RUN set -ex \
    && apk add --no-cache ffmpeg libmagic gettext \
    && apk add --no-cache --virtual .build-deps python3-dev  postgresql-dev gcc make libc-dev zlib-dev jpeg-dev \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps

# Copy project
ADD app /app

# Change to the directory containing manage.py for running Django commands
WORKDIR /app

# Add virtualenv to path
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Set communication port
EXPOSE 8000

CMD ["gunicorn", "GEN.asgi:application", "--bind", ":8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]
