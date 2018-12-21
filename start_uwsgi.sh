#!/bin/bash

export APP_SETTINGS=app.config.ProductionConfig

nohup uwsgi uwsgiconfig.ini &
