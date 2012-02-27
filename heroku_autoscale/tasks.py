from time import sleep

from heroku_autoscale import MissingParameter
from heroku_autoscale.models import HerokuAutoscaler

autoscale = HerokuAutoscaler()


def start_heartbeat(settings=None):
    print settings
    print settings.HEARTBEAT_INTERVAL_IN_SECONDS
    try:
        assert settings.HEARTBEAT_INTERVAL_IN_SECONDS is not None
    except:
        raise MissingParameter("HEARTBEAT_INTERVAL_IN_SECONDS not set.")

    while True:
        beat()
        sleep(settings.HEARTBEAT_INTERVAL_IN_SECONDS)


def beat():
    autoscale.full_heartbeat()
