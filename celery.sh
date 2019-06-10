#!/bin/sh

celery worker -A celery_worker --loglevel=info -Q rmxbot
