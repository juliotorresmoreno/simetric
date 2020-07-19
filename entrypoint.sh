#!/bin/sh

export `cat .env | grep "^[^#]" | xargs`

gunicorn simetric.wsgi --workers 4 -b 0.0.0.0:8000
