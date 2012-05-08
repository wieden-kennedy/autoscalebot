import time
import urllib2
from heroku_web_autoscale.backends.measurement.base import BaseMeasurementBackend
from heroku_web_autoscale.logger import logger


class ResponseTimeBackend(BaseMeasurementBackend):
    """
    This backend measures the amount of time a url takes to respond.

    It accepts the following parameters:

    measurement_url, which defaults to "/heroku-autoscale/measurement/", and
    max_response_time_in_seconds, which defaults to 30.

    It returns a dictionary, with the following format:

    {
        'backend': 'ResponseTimeBackend',
        'data': 350, // ms
        'success': True,  // assuming it was
    }
    """
    def __init__(self, *args, **kwargs):
        super(ResponseTimeBackend, self).__init__(*args, **kwargs)
        self.url = kwargs.get("measurement_url", "/heroku-autoscale/measurement/")
        self.max_response_time_in_seconds = kwargs.get("max_response_time_in_seconds", 30)

    def measure(self, *args, **kwargs):
        start_time = time.time()
        success = True

        try:
            response = urllib2.urlopen(self.url, None, self.max_response_time_in_seconds)
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
            logger.debug("Error getting response from %s." % self.url)

        return {
            'backend': 'ResponseTimeBackend',
            'data': diff,
            'success': success
        }
