from base import TOO_LOW, TOO_HIGH, JUST_RIGHT, logger
from celery.events.snapshot import Polaroid
from celery.events.state import State
from heroku_web_autoscale.backends.measurement.base import BaseMeasurementBackend

class Camera(Polaroid):
    pass


class CeleryRedisQueueSizeBackend(BaseMeasurementBackend):
    def __init__(self, autoscaler, settings, *args, **kwargs):
        """
        """
        super(CeleryRedisQueueSizeBackend, self).__init__()

    def heartbeat(self):
        """
        """
        state = State()

        pass
