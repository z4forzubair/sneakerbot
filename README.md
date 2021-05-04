# SneakerBot

## Stack Details
Python = 3.8

Django = 3.2.1

Postgres = 11

## Setup Project

### Create Database
This project uses Postgres database. Database should be created or restored from dump.
Database configurations are stored in `sneakerbot_backend/local_settings.py` which are being imported in main 
`sneakerbot_backend/settings.py` file.

`local_settings.py` should have this object as per local configurations.

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'database-name',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Run Project
Once database is set up, use following commands.

**Apply Migrations**

`python manage.py migrate`

**Run Server**

`python manage.py runserver`

**Create Super User**

`python manage.py createsuperuser`

Super user created at this step will help you log-in to admin side of site. 

Admin side can be accessed at `/admin` of server url.
