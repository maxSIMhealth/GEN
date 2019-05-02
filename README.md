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
