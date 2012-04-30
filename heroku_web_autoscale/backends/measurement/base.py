from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH
from heroky_web_autoscale.logger import logger

class BaseMeasurementBackend(object):
    """
    
    """
    def __init__(self, autoscaler, settings):
        self.autoscaler = autoscaler
        self.settings = settings

    def heartbeat(self):
        raise NotImplemented("Not Implemented!!!")
