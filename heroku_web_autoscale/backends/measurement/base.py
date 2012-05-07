from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH, NotYetImplementedException
from heroku_web_autoscale.logger import logger


class BaseMeasurementBackend(object):
    """
    This is the base measurement class. It should be subclasses to write custom backends.

    The measurement backend is expected to provide a get_scaling_need function that
    returns TOO_LOW, TOO_HIGH, or JUST_RIGHT.

    """
    def __init__(self, autoscaler, settings, min_time=500, max_time=1000, post_scale_wait_time=0):
        self.autoscaler = autoscaler
        self.settings = settings

    def _measure(self, *args, **kwargs):
        raise NotYetImplementedException

    def _respond(self, *args, **kwargs):
        raise NotYetImplementedException

    def get_scaling_need(self, *args, **kwargs):
        raise NotYetImplementedException
