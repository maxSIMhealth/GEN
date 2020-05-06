# GEN - Gamified Educational Network

## Installation instructions
- Clone this repo
- This project is based on python 3.x, and I recommend using a python environment tool such as [virtualenv](https://virtualenv.pypa.io/en/stable/):
```
# venv should be included in python3 by default
# otherwise, check your distro for installing instructions
python -m venv venv
source venv/bin/activate
```
- Create a `.env` file based on `.env-example`
- Instal project dependencies: `pip install -r requirements.txt`
- Generate database: `python manage.py migrate`
- Create a super user: `python manage.py createsuperuser --username USERNAME --email USER_EMAIL`
- Install dependencies: `sudo apt install ffmpeg`
- Run the project: `python manage.py runserver`

## General settings
`WIP: these groups will be used to set permissions, and later they will be automatically created while generating the database`
- Create the following groups in the admin page:
  - admin
  - instructor

## Production

### Install packages
- Install nginx (use your distro install command, e.g., `sudo apt install nginx`)
- Install gunicorn: `pip install gunicorn`

### NGINX
- Create `/etc/nginx/sites-available/GEN` with the following content:
```
server {
        listen 80 default_server;
        #server_name gen.test.ca;
        access_log off;
        location /static/ {
                # files that will be gathered by manage.py collecstatic
                alias /opt/GEN_static/;
        }
	location /media/ {
		# media files uploaded by users
		alias /opt/GEN_media/;
	}
        location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header X-Forwarded-Host $server_name;
                proxy_set_header X-Real-IP $remote_addr;
                add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
		client_max_body_size 300M;
        }
}
```
- Create static files directory: `sudo mkdir /opt/GEN_static/`
- Create media files directory: `sudo mkdir /opt/GEN_media/`
- Change ownership of static and media directories to user that will run GEN (e.g., `sudo chown user:usergroup /opt/GEN_static`
- Enable GEN on nginx: `sudo ln -s /etc/nginx/sites-available/GEN /etc/nginx/sites-enabled/GEN`
- Remove default nginx site (if it exists): `sudo rm /etc/nginx/sites-enabled/default`
- Restart service: `sudo service nginx restart`

### GEN settings
- Edit `GEN/settings.py` and modify the following:
  - add `STATIC_ROOT=/opt/GEN_static/` before `STATIC_URL`
  - change `MEDIA_ROOT` to `/opt/GEN_media/`
- Edit `.env` and set `DEBUG=False`y
- Colllect static files: `python manage.py collectstatic`

### Start the server
- Gunicorn: `gunicorn GEN.wsgi`
