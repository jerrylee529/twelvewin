#!/bin/bash

export APP_SETTINGS=app.config.DevelopmentConfig


python manage.py runserver -h 0.0.0.0 -p 8088
