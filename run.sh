#!/bin/sh

export FLASK_ENV=development
export FLASK_APP=run.py

flask run -p 8000 --host=0.0.0.0
