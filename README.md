This project is a Test Driven Python (Django and Django Rest Framework with gitlab CI/CD) implementation of a real world electronics store use case

-> The store has branches and the data is partitioned by the shop/enterprise code

The project is built on python 3.9. To set up this python version, refer to the `python_installation.sh` script in the project and run it on your linux machine.

To get started set up a virtualenv

[Virtualenv with Virtualenvwrapper](https://www.freecodecamp.org/newsvirtualenv-with-virtualenvwrapper-on-ubuntu-18-04/)

-> Replace RETAIL-PORTAL with your virtualenv

    mkvirtualenv -p python3.9 RETAIL-PORTAL

If you have a virtual environment set up.

    workon <your virtualenv>

    python manage.py migrate

    python manage.py load_default_data

    python manage.py shell

Once the shell has loaded enter

    exec(open('setup_data.py').read())

    exit()

`python manage.py load_default_data` command loads the default data

Executing the `setup_data.py` script loads the development data

Now since everything is set up run the server

    python manage.py runserver

You should be set now

The project uses JWT authentication. To authenticate hit the /api/token/ endpoint with the payload

    {
        "email": "adminuser@email.com",
        "password": "Hu46!YftP6^l$"
    }

Use the access token generated for authentication

By default the project uses an sqlite database.

However, to use postgres source the env.sh file (Run `source env.sh`) and have the database set up

## DATABASE SETUP

    sudo -u postgres psql

    CREATE DATABASE retail_db;

    CREATE USER elites_user WITH PASSWORD 'elites_pass';

    ALTER ROLE elites_user SET client_encoding TO 'utf8';
    ALTER ROLE elites_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE elites_user SET timezone TO 'UTC';

    GRANT ALL PRIVILEGES ON DATABASE retail_db TO elites_user;

    \q

# Other Set ups

## To use Ngrok

    ngrok http 8000


## Redis

#### On Ubuntu

    sudo apt install redis

    brew install redis

<!-- Run redis server -->

    redis-server --port 6380 --replicaof 127.0.0.1 6379

<!-- Monitor redis -->

    redis-cli monitor

<!-- Start Celery -->
### Celery

    python -m celery -A elites_retail_portal.config worker

    python -m celery -A elites_retail_portal.config worker -l info

#### On Windows

https://developer.redis.com/create/windows/


## Additional notes

    -> To delete other branches and keep master branch use

    git branch | grep -v "master" | xargs git branch -D

