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

- Install dependencies: `sudo apt install -y postgresql postgresql-contrib python3-dev python3-venv libpq-dev ffmpeg`
- Clone this repo and access the repo directory: `cd GEN`
- Create a virtual environment: `python3 -m venv venv`
- Activate virtual environment: `source venv/bin/activate`
- Create a `.env` file based on `conf-templates/env` (read the instructions in the file)
- Install project dependencies: `pip install -r requirements.txt`
- Generate database: `python manage.py migrate`
- Create a super user: `python manage.py createsuperuser --username USERNAME --email USER_EMAIL`
- Run the project: `python manage.py runserver`

### Possible issues
- If you get a error message about _libmagic_ (`ImportError: failed to find libmagic.  Check your installation`), try running these commands:
    ```
    pip uninstall python-magic
    pip install python-magic-bin
    ```

## Locale (i18n) messages
- Install GNU gettext: `sudo apt install gettext`
- This project is currently configured to support *en* and *fr*
- To regenerate locale messages for French (fr) run:
  ```
  python manage.py makemessages -l 'fr' --ignore venv --ignore static
  python manage.py makemessages -l 'fr' -d djangojs --ignore bootstrap.min.js
  ```
    - The first command generates strings based on python and html files. The *--ignore* flag is necessary to make it ignore the venv (virtualenv) directory.
    - The second command generates strings based on javascript files. The *--ignore* flag is necessary because bootstrap causes an error that interrupts the command.
- Now compile the messages: `python manage.py compilemessages`
- The `.po` files will be at `locale/*language_code*/LC_MESSAGES`. For example, `locale/fr/LC_MESSAGES/django.po`.
- Access `/rosetta` to translate the `.po` files

### Using django-modeltranslation
- Create a `translation.py` file in the app directory
- Register a `TranslationOptions` for every model you want to translate. For example:
  ```
  from modeltranslation.translator import TranslationOptions, translator
  from .models import Course

  class CourseTranslationOptions(TranslationOptions):
    fields = ("name", "description")

  translator.register(Course, CourseTranslationOptions)
  ```
- Sync the database using `python manage.py makemigrations` and `python manage.py migrate`
- If the model already existed and had data, you will need to initialize the default translation, otherwise the template (and admin) will show the translated value of the field, which will be empty: `python manage.py update_translation_fields`
- For more information, access [django-modeltranslation documentation](https://django-modeltranslation.readthedocs.io)

## Production
For a detailed step-by-step instructions on how deploy Django, check this guide: [How To Set Up Django with Postgres, Nginx, and Gunicorn on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04)

### Dependencies
- Install dependencies: `sudo apt install -y build-essential nginx postgresql postgresql-contrib python3-dev python3-venv libpq-dev ffmpeg`
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
- Install project dependencies: `pip install -r requirements.txt`

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
- Add server domain and IP to allowed hosts list in `.env`
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
(This section is only relevant if you are using UFW)
- Allow nginx connections: `sudo ufw allow 'Nginx Full'`
  - This will enable ports 80 (http) and 443 (https)
- If you are using ssh, be sure to also enable it: `sudo ufw allow ssh`
- Now enable UFW: `sudo ufw enable`
- Check UFW status: `sudo ufw status`

### Set up SSL
- GEN for production is configured to use only https, so you will need to set up SSL
- We are going to use Certbot to generate a certificate via [Let's Encrypt](https://letsencrypt.org/). For instructions tailored to your specific system, check https://certbot.eff.org/
- Make sure your DNS records point to your server's public IPv4 and IPv6 addresses.
- Enable the universe repository:
  ```
  sudo apt-get update
  sudo apt-get install software-properties-common
  sudo add-apt-repository universe
  sudo apt-get update
  ```
- Install Certbot: `sudo apt-get install certbot python3-certbot-nginx`
- Run this command to get a certificate and have Certbot edit your Nginx configuration automatically to serve it, turning on HTTPS access in a single step: `sudo certbot --nginx`
  - When asked, choose **YES** to redirect HTTP traffic to HTTPS.
- Test automatic renewal: `sudo certbot renew --dry-run`
- Confirm that Certbot worked by visiting https://www.ssllabs.com/ssltest/

### Set up Sendgrid
- When a user sets up a new account, GEN will send a verification email to validate the user's email address. For this purpose, we are using Sendgrid but you are free to use any other method. For detailed instructions on using sendgrid, check this guide: [Sending Emails with Django using SendGrid in 3 easy steps](https://simpleit.rocks/python/django/adding-email-to-django-the-easiest-way/) (this part of the README is based on it).
- Set up an account on [Sendgrid](https://app.sendgrid.com/)
- Create an API key for the app at https://app.sendgrid.com/settings/api_keys
  - In name enter something like `GEN_send_mails`
  - Choose **Restricted Access**, enable **Mail Send** and hit the **Create** button
- Edit `.env` and set the variable `SENDGRID_API_KEY` with the generated API key
- Set up **Sender authentication** on Sendgrid: https://app.sendgrid.com/settings/sender_auth
- Check it is working:
  ```
  python manage.py shell
  > from django.core.mail import send_mail
  > send_mail('testing', 'my message', 'hello@serverdomain.com', ['personal@example.com'], fail_silently=False)
  ```
  - If you see a message similar to `Sendgrid email backend is in sandbox mode!  Emails will not be delivered.` it means everything is ok.
  - If you get an HTTP 403 Error you probably didn't set up **Sender authentication**.
- To send a test email:
   ```
  python manage.py shell
  > from django.core.mail import send_mail
  > from django.conf import settings
  > settings.SENDGRID_SANDBOX_MODE_IN_DEBUG=False
  > send_mail('testing', 'my message', 'hello@serverdomain.com', ['personal@example.com'], fail_silently=False)
  ```
  - If the command was successful, the output will be `1` and you should get an email.


### Start/stop the server
- Start: `sudo systemctl start gunicorn`
- Stop: `sudo systemctl stop gunicorn.socket gunicorn.service`

### Maintenance mode
- Use the following command to enable/disable maintenance mode while the server is up: `python manage.py maintenance_mode on|off`
- When activated, the server will return a 503 status and render a warning page (`templates/503.html`).
- The admin site will not be affected by the maintenance-mode status, but that can changed on the `setting.py` file.

# Contributors
The previous iteration of GEN was called [OPEN](https://www.github.com/mangobug/OPEN) and was developed by [Zain Kahn](https://github.com/mangobug). GEN is currently being developed by [Andrei B. B. Torres](https://www.github.com/andreibosco/).  
