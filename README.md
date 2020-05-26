# GEN - Gamified Educational Network

## Dependencies
- PostgreSQL
- Python 3.x
  - I recommend using a python environment tool such as [virtualenv](https://virtualenv.pypa.io/en/stable/):
    ```
    # venv should be included in python3 by default
    # otherwise, check your distro for installing instructions
    python -m venv venv
    source venv/bin/activate
    ```

## General instructions
- **Note:** these instructions are for Ubuntu 20.04 LTS.

### PostgreSQL
- Switch to postgres user: `sudo su - postgres`
- Create database user: `createuser u_gen`
- Create a new database and set the user as the owner: `createdb django_gen --owner u_gen`
- Define a strong password for the user: `psql -c "ALTER USER u_gen WITH PASSWORD 'PUT_DB_USER_PASSWORD_HERE'"`
- Exist postgres user: `exit`
- Edit `.env`, uncomment `DATABASE_URL` line and update it with your postgresql server settings (default port is 5432)

### Notes
- On development mode (`DEBUG`), no email is sent and the output is echoed into stdout.
#### WIP
`these groups will be used to set permissions, and later they will be automatically created while generating the database`
- Create the following groups in the admin page:
  - admin
  - instructor

## Development

- Install dependencies: `sudo apt install -y postgresql postgresql-contrib python-dev libpq-dev ffmpeg`
- Clone this repo and access the repo directory: `cd GEN`
- Create a virtual environment: `python3 -m venv venv`
- Activate virtual environment: `source venv/bin/activate`
- Create a `.env` file based on `conf-templates/env` (read the instructions in the file)
- Instal project dependencies: `pip install -r requirements.txt`
- Generate database: `python manage.py migrate`
- Create a super user: `python manage.py createsuperuser --username USERNAME --email USER_EMAIL`
- Run the project: `python manage.py runserver`

## Production
For a detailed step-by-step instructions on how deploy Django, check this guide: [How To Set Up Django with Postgres, Nginx, and Gunicorn on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04)

### Dependencies
- Install dependencies: `sudo apt install -y build-essential nginx postgresql postgresql-contrib python3-dev libpq-dev ffmpeg`
  - **Note:** if you are using a different version of python than your distro default, install the correct dev package (e.g.: `python3.8-dev`)

### Create user
- This user will be used exclusively to run GEN:
- Create user: `adduser gen`

### Clone GEN
- As user `gen`, clone this repo
- Access GEN directory: `cd GEN`
- Create a virtual environment: `python3 -m venv venv`
- Activate virtual environment: `source venv/bin/activate`
- Create a `.env` file based on `conf-templates/env` (read the instructions in the file)
- Instal project dependencies: `pip install -r requirements.txt`

### PostgreSQL
- Switch to postgres user: `sudo su - postgres`
- Create database user: `createuser u_gen`
- Create a new database and set the user as the owner: `createdb django_gen --owner u_gen`
- Start postgresql prompt: `psql`
  - Define a strong password for the user: `ALTER USER u_gen WITH PASSWORD 'PUT_DB_USER_PASSWORD_HERE';`
  - Set the default encoding to UTF-8: `ALTER ROLE u_gen SET client_encoding TO 'utf8';`
  - Set the default transaction isolation scheme to “read committed”, which blocks reads from uncommitted transactions: `ALTER ROLE u_gen SET default_transaction_isolation TO 'read committed';`
  - Set timezone to UTC: `ALTER ROLE u_gen SET timezone TO 'UTC';`
  - Exit postgresql prompt: `\q`
- Exit postgres user: `exit`
- Edit `.env`, uncomment `DATABASE_URL` line and update it with your postgresql server settings (default port is 5432)

### Set up GEN database and superuser (admin)
- Generate database:
  ```
  python manage.py makemigrations
  python manage.py migrate
  ```
- Create a super user: `python manage.py createsuperuser --username USERNAME --email USER_EMAIL`

### GEN settings
- Create static files directory: `mkdir /home/gen/GEN_static/`
- Create media files directory: `mkdir /home/gen/GEN_media/`
- If necessary, change ownership of static and media directories to user that will run GEN (e.g., `sudo chown user:usergroup /home/gen/GEN_static`
- Add server domain or IP to allowed hosts list in `.env`
- Open `GEN/settings.py` and check if `STATIC_ROOT` and `MEDIA_ROOT` and pointing to the correct locations
- Edit `.env` and set `DEBUG=False`
- Collect static files: `python manage.py collectstatic`

### Gunicorn
- We will use systemd service and socket files to manage gunicorn and start/stop GEN
- Install gunicorn: `pip install gunicorn`
  - **Note:** if you are using virtualenv, don't forget to enable it **BEFORE** using pip
- Copy the files on `GEN/conf-templates/systemd` to `/etc/systemd/system/`
- Update the paths in the files, if necessary
- Start and enable gunicorn socket so that it is created on boot:
  ```
  sudo systemctl start gunicorn.socket
  sudo systemctl enable gunicorn.socket
  ```
- To check gunicorn socket status: `sudo systemctl status gunicorn.socket`
- To verify the socket file: `file /run/gunicorn.socket`. It should output something like this:
  ```
  /run/gunicorn.sock: socket
  ```
- In case of an error, check gunicorn socket log: `sudo journalctl -u gunicorn.socket`

### Nginx
- Copy `GEN/conf-templates/nginx/GEN` to `/etc/nginx/sites-available/GEN`
- Update the paths in the file, if necessary
- Enable GEN on nginx: `sudo ln -s /etc/nginx/sites-available/GEN /etc/nginx/sites-enabled/GEN`
- Test your nginx conf file for syntax errors: `sudo nginx -t`
- Remove default nginx site (if it exists): `sudo rm /etc/nginx/sites-enabled/default`
- Restart service: `sudo systemctl restart nginx`

### UFW (firewall)
(This section is only relevant if you ar eusing UFW)
- Allow nginx connections: `sudo ufw allow 'Nginx Full'`
  - This will enable ports 80 (http) and 443 (https)
- If you are using ssh, be sure to also enable it: `sudo ufw allow ssh`
- Now enable UFW: `sudo ufw enable`
- Check UFW status: `sudo ufw status`

### Start/stop the server
- Start: `sudo systemctl start gunicorn`
- Stop: `sudo systemctl stop gunicorn.socket gunicorn.service`
