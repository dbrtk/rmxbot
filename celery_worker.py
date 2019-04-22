"""
This module only imports the instance of celery created on the level of
rmxbot.app.

The celery isntance is configured within rmxbot.app. On this level, it is made
available to the celery worker.

This command will run the celery worker:
`celery -A rmxbot.celery_worker worker --loglevel=info`
or
`celery -A rmxbot.celery_worker worker --loglevel=debug`
(for a more verbose standard output).
"""

from rmxbot.app import celery

celery = celery
