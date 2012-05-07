from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH
from heroku_web_autoscale.logger import logger

from heroku_web_autoscale.backends.measurement import BaseMeasurementBackend


class AppDecisionBackend(BaseMeasurementBackend):
    """

    """
    def __init__(self, autoscaler, settings, min_time=500, max_time=1000, post_scale_wait_time=0, *args, **kwargs):
        super(AppDecisionBackend, self).__init__(*args, **kwargs)
        self.autoscaler = autoscaler
        self.settings = settings

    def heartbeat(self):
        raise NotImplemented("Not Implemented!!!")
