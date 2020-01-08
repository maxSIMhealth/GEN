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
- Create a super user: `python manage.py createsuperuser`
- Run the project: `python manage.py runserver`

## Locale (i18n) messages
- This project is currenctly configured to support *en* and *fr*
- To regenerate locale messages for French (fr) run: `python manage.py makemessages -l 'fr' --ignore venv --ignore static`
  - The *-i* flag is necessary to make it ignore the venv (virtualenv) directory
- And to compile it, go to the locales directory and run: `python ../manage.py compilemessages`
  - You **SHOULD NOT** run `compilemessages` from the project main directory, because it will try to compile the translation messages for all of the packages at *venv* directory.

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
        location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header X-Forwarded-Host $server_name;
                proxy_set_header X-Real-IP $remote_addr;
                add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
        }
}
```
- Create static files directory: `sudo mkdir /opt/GEN_static/`
- Enable GEN on nginx: `sudo ln -s /etc/nginx/sites-available/GEN /etc/nginx/sites-enabled/GEN`
- Restart service: `sudo service nginx restart`

### GEN settings
- Edit `GEN/settings.py` and add `STATIC_ROOT=/opt/GEN_static/` before `STATIC_URL`
- Edit `.env` and set `DEBUG=False`
- Colllect static files: `python manage.py collectstatic`

### Start the server
- Gunicorn: `gunicorn GEN.wsgi`
