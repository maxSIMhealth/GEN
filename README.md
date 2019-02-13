# OPEN2 - Educational networking web site for research purposes

## Installation instructions
- Clone this repo
- This project is based on python 3.x, and I recommend using a python environment tool such as [virtualenv](https://virtualenv.pypa.io/en/stable/):
```
pip install virtualenv
python -m venv venv
source venv/bin/activate
```
- Create a `.env` file based on `.env-example`
- Instal project dependencies: `pip install -r requirements.txt`
- Generate database: `python manage.py migrate`
- Create a super user: `python manage.py createsuperuser`
- Run the project: `python manage.py runserver`
