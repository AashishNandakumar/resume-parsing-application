#!/bin/bash

redis-server --daemonize yes

celery -A resume_parsing_application worker --loglevel=info &

python manage.py runserver 0.0.0.0:8000
