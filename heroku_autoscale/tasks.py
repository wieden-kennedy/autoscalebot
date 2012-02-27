from datetime import timedelta
from celery.decorators import periodic_task
from django.conf import settings


@periodic_task(run_every=timedelta(seconds=settings.AUTOSCALE_HEARTBEAT_INTERVAL_IN_SECONDS))
def beat():
    pass
