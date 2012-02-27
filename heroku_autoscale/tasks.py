# from datetime import timedelta
from time import sleep

# from celery.decorators import periodic_task

from heroku_autoscale import MissingParameter
from heroku_autoscale.models import AutoscaleManager
from heroku_autoscale.conf import settings

autoscale = AutoscaleManager()


def start_heartbeat():
    try:
        assert settings.HEARTBEAT_INTERVAL_IN_SECONDS is not None
    except:
        raise MissingParameter("AUTOSCALE_HEARTBEAT_INTERVAL_IN_SECONDS not set.")

    while True:
        beat()
        sleep(settings.HEARTBEAT_INTERVAL_IN_SECONDS)


# @periodic_task(run_every=timedelta(seconds=settings.HEARTBEAT_INTERVAL_IN_SECONDS))
def beat():
    autoscale.scale_dynos()
