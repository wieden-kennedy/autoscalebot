from base import BaseMeasurementBackend, TOO_LOW, TOO_HIGH, JUST_RIGHT, logger
from celery.events.snapshot import Polaroid
from celery.events.state import State

class Camera(Polaroid):
    pass

class CeleryQueueSizeBackend(BaseMeasurementBackend):
    def __init__(self, autoscaler, settings, *args, **kwargs):
        """
        """
        super(CeleryQueueSizeBackend, self).__init__()

    def heartbeat(self):
        """
        """
        state = State()
        
        pass
        
