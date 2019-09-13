## django-rest-recipe-api

#####Install dependencies

    $ pip install -r requirements.txt
#####Make migrations & migrate

    $ python manage.py makemigrations && python manage.py migrate
#####Create Super user
    
    $ python manage.py createsuperuser

#####Launching the app
    $ python manage.py runserver

#####Run Tests
    $ python manage.py test -v 2

#####Help Commands
    $ docker build .
    $ docker-compose build
    $ docker-compose run app sh -c "django-admin startproject app ."
    $ docker-compose run app sh -c "python manage.py test -v 2 && flake8"
    $ docker-compose run app sh -c "python manage.py startapp core"
    $ docker-compose run app sh -c "python manage.py makemigrations && python manage.py migrate"
    $ docker-compose up
    $ docker-compose run app sh -c "python manage.py createsuperuser"
    $ docker-compose run --rm app sh -c "python manage.py startapp user"
    $ docker-compose run --rm app sh -c "python manage.py startapp recipe"

