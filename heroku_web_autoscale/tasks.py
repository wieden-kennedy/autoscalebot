from time import sleep

from heroku_web_autoscale import MissingParameter
from heroku_web_autoscale.conf import AutoscaleSettings
from heroku_web_autoscale.models import HerokuAutoscaler


def start_autoscaler(settings=None, in_django=False):
    settings = AutoscaleSettings(settings=settings, in_django=in_django)
    autoscale = HerokuAutoscaler(settings)

    try:
        assert settings.HEARTBEAT_INTERVAL_IN_SECONDS is not None
    except:
        raise MissingParameter("HEARTBEAT_INTERVAL_IN_SECONDS not set.")

    while True:
        autoscale.full_heartbeat()
        sleep(settings.HEARTBEAT_INTERVAL_IN_SECONDS)