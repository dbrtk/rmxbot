#!/bin/sh

celery -A celery_worker worker --loglevel=INFO -Q rmxbot

