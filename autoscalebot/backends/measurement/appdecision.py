import json
import urllib2
from autoscalebot import TOO_LOW, JUST_RIGHT, TOO_HIGH
from autoscalebot.logger import logger

from autoscalebot.backends.measurement.base import BaseMeasurementBackend


class AppDecisionBackend(BaseMeasurementBackend):
    """
    This backend returns the json-encoded data from a measurement url response.

    It accepts the following parameters:

    MEASUREMENT_URL, which defaults to "/autoscalebot/measurement/", and
    MAX_RESPONSE_TIME_IN_SECONDS, which defaults to 30.

    It returns a dictionary, with the following format:

    {
        'backend': 'AppDecisionBackend',
        'data': {
            'custom-key-from-url": 'custom val from url',
        },
        'success': True,  // assuming it was
    }
    """

    def __init__(self, *args, **kwargs):
        BACKEND_SETTINGS = {
            "MEASUREMENT_URL": "/autoscalebot/measurement/",
            "MAX_RESPONSE_TIME_IN_SECONDS": 30,
        }
        super(AppDecisionBackend, self).__init__(*args, **kwargs)
        self.settings = BACKEND_SETTINGS.update(self.settings)

    def measure(self, *args, **kwargs):
        success = True

        try:
            response = urllib2.urlopen(self.settings.MEASUREMENT_URL, None, self.settings.MAX_RESPONSE_TIME_IN_SECONDS)
            json_resp = response.read()
            assert json_resp is not None
            app_dict = json.loads(json_resp)

        except:  # probably URLError, but anything counts.
            success = False

        return {
            'backend': 'AppDecisionBackend',
            'data': app_dict,
            'success': success
        }