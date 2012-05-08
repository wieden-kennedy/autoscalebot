from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH, NotYetImplementedException
from heroku_web_autoscale.logger import logger

from heroku_web_autoscale.backends.scaling.base import BaseScalingBackend


class HerokukScalingBackend(BaseScalingBackend):
    """
    This is the base scaling class
    """
    def __init__(self, autoscaler, settings, min_time=500, max_time=1000, post_scale_wait_time=0):
        self.autoscaler = autoscaler
        self.settings = settings
