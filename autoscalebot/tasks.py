from time import sleep

from autoscalebot import MissingParameter
from autoscalebot.conf import AutoscaleSettings
from autoscalebot.models import HerokuAutoscaler


def start_autoscaler(settings=None, in_django=False):
    settings = AutoscaleSettings(settings=settings, in_django=in_django)
    autoscale = HerokuAutoscaler(settings)

    try:
        assert settings.HEARTBEAT_INTERVAL_IN_SECONDS is not None
    except:
        raise MissingParameter("HEARTBEAT_INTERVAL_IN_SECONDS not set.")

    while True:
        last_heartbeat_time_in_seconds = autoscale.full_heartbeat() / 1000
        next_interval = settings.HEARTBEAT_INTERVAL_IN_SECONDS - last_heartbeat_time_in_seconds
        if next_interval > 0:
            sleep(next_interval)
