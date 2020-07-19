#!/bin/sh

celery worker -A celery_worker --loglevel=info -Q rmxbot

# /opt/program/env/bin/celery worker -A celery_worker --loglevel=info -Q rmxbot