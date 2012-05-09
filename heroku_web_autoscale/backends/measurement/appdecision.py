import json
import urllib2
from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH
from heroku_web_autoscale.logger import logger

from heroku_web_autoscale.backends.measurement.base import BaseMeasurementBackend


class AppDecisionBackend(BaseMeasurementBackend):
    """
    This backend returns the json-encoded data from a measurement url response.

    It accepts the following parameters:

    measurement_url, which defaults to "/heroku-autoscale/measurement/", and
    max_response_time_in_seconds, which defaults to 30.

    It returns a dictionary, with the following format:

    {
        'backend': 'AppDecisionBackend',
        'data': {
            'custom-key-from-url": 'custom val from url',
        },
        'success': True,  // assuming it was
    }
    """

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
