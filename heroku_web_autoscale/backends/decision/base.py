from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH, NotYetImplementedException
from heroku_web_autoscale.logger import logger


class BaseDecisionBackend(object):
    """
    This is the base decision backend.
    """
    def __init__(self, autoscaler, settings, min_time=500, max_time=1000, post_scale_wait_time=0):
        pass
