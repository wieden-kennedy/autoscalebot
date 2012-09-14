import json
import urllib2
from autoscalebot import TOO_LOW, JUST_RIGHT, TOO_HIGH
from autoscalebot.logger import logger

from autoscalebot.backends.measurement.base import BaseMeasurementBackend


class AppDecisionBackend(BaseMeasurementBackend):
    """
    This backend returns the json-encoded data from a measurement url response.

    It accepts the following parameters:

    Its measure method returns a dictionary, with the following format:

    {
        'backend': 'AppDecisionBackend',
        'data': {
            'custom-key-from-url": 'custom val from url',
        },
        'success': True,  // assuming it was
    }
    """

    def default_settings(self):
        base_defaults = super(self, "default_settings")()
        base_defaults.update({
            "url": "/autoscalebot/custom-measurement-url/",
            "timeout_in_seconds": 30,
        })
        return base_defaults

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
