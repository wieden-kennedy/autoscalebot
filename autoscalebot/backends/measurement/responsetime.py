import time
import urllib2
from autoscalebot.backends.measurement.base import BaseMeasurementBackend
from autoscalebot.logger import logger


class ResponseTimeBackend(BaseMeasurementBackend):
    """
    This backend measures the amount of time a url takes to respond.

    It accepts the following parameters:

    MEASUREMENT_URL, which defaults to "/autoscalebot/measurement/", and
    MAX_RESPONSE_TIME_IN_SECONDS, which defaults to 30.

    Its measure method returns a dictionary, with the following format:

    {
        'backend': 'ResponseTimeBackend',
        'data': 350, // ms
        'success': True,  // assuming it was
    }
    """

    def __init__(self, *args, **kwargs):
        self.DEFAULT_BACKEND_SETTINGS = {
            "MEASUREMENT_URL": "/autoscalebot/measurement/",
            "MAX_RESPONSE_TIME_IN_SECONDS": 30,
        }
        super(ResponseTimeBackend, self).__init__(*args, **kwargs)

    def measure(self, *args, **kwargs):
        start_time = time.time()
        success = True

        try:
            response = urllib2.urlopen(self.settings.MEASUREMENT_URL, None, self.settings.MAX_RESPONSE_TIME_IN_SECONDS)
            assert response.read(1) is not None
        except:  # probably URLError, but anything counts.
            success = False

        if success:
            end_time = time.time()
            diff = end_time - start_time
            diff = diff * 1000
            logger.debug("Response time: %sms." % diff)
        else:
            diff = 0
            logger.debug("Error getting response from %s." % self.settings.MEASUREMENT_URL)

        return {
            'backend': 'ResponseTimeBackend',
            'data': diff,
            'success': success
        }
