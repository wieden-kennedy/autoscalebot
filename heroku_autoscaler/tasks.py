from time import sleep

from heroku_autoscale import MissingParameter
from heroku_autoscale.models import HerokuAutoscaler

autoscale = HerokuAutoscaler()


def start_heartbeat(settings=None):
    if not settings:
        from heroku_autoscale.conf import settings

    try:
        assert settings.HEARTBEAT_INTERVAL_IN_SECONDS is not None
    except:
        raise MissingParameter("HEARTBEAT_INTERVAL_IN_SECONDS not set.")

    while True:
        autoscale.full_heartbeat()
        sleep(settings.HEARTBEAT_INTERVAL_IN_SECONDS)
