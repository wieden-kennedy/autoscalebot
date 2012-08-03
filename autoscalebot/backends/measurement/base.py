from autoscalebot import NotYetImplementedException
from autoscalebot.backends import BaseBackend
from autoscalebot.util import Struct


class BaseMeasurementBackend(BaseBackend):
    """
    This is the base measurement class. It should be subclassed to write custom backends.

    The measurement backend is expected to provide a measure method that
    evaluates the load on the app, and returns a dictionary with the following format:

    {
        'backend': 'BackendClassName',
        'data': "some_data_of_any_type"
    }

    """

    def __init__(self, *args, **kwargs):
        self.DEFAULT_BASE_SETTINGS = {}
        super(BaseMeasurementBackend, self).__init__(*args, **kwargs)

    def measure(self, *args, **kwargs):
        raise NotYetImplementedException

    @property
    def settings(self):
        return self.autoscalebot.settings.MEASUREMENT.SETTINGS
