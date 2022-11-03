Setup a virtualenv

[Virtualenv with Virtualenvwrapper](https://www.freecodecamp.org/newsvirtualenv-with-virtualenvwrapper-on-ubuntu-18-04/)

    mkvirtualenv -p python3.9 FRANCHISE-PORTAL

If you have a virtual environment set up.

    workon <your virtualenv>

    python manage.py migrate

    python manage.py shell

Once the shell has loaded enter

    exec(open('setup_data.py').read())

    exec(open('default_data.py').read())

    exit()

Default data is loaded

    python manage.py runserver

You should be set now

### Ngrok

    ngrok http 8000

### Install redis

#### On Ubuntu

    sudo apt install redis

    brew install redis

<!-- Run redis server -->

    redis-server --port 6380 --replicaof 127.0.0.1 6379

<!-- Monitor redis -->

    redis-cli monitor

<!-- Start Celery -->
### Celery

    python -m celery -A elites_franchise_portal.config worker

    python -m celery -A elites_franchise_portal.config worker -l info

#### On Windows

https://developer.redis.com/create/windows/

### Ignore this

    echo 'export PATH="/home/gathua/.ebcli-virtual-env/executables:$PATH"' >> ~/.bash_profile && source ~/.bash_profile

    git branch | grep -v "master" | xargs git branch -D

    scrcpy


## DATABASE SETUP

    sudo -u postgres psql

    CREATE DATABASE elites_franchise;

    CREATE USER elites_user WITH PASSWORD 'elites_pass';

    ALTER ROLE elites_user SET client_encoding TO 'utf8';
    ALTER ROLE elites_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE elites_user SET timezone TO 'UTC';

    GRANT ALL PRIVILEGES ON DATABASE elites_franchise TO elites_user;

    \q


xrandr -o left
xrandr -o normal
