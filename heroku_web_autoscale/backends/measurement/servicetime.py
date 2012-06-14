import re
import urllib2
from heroku_web_autoscale.backends.measurement.base import BaseMeasurementBackend
from heroku_web_autoscale.logger import logger


class HerokuServiceTimeBackend(BaseMeasurementBackend):
    """
    This backend measures the amount of time a url takes to respond.

    It accepts the following parameters:

    HEROKU_APP, which is a heroku app object from the heroku library (optional:
                it will use the app derived from the scaling backend if left out),
    MEASUREMENT_URL, which defaults to "/heroku-autoscale/measurement/", and
    MAX_RESPONSE_TIME_IN_SECONDS, which defaults to 30.

    It returns a dictionary, with the following format:

    {
        'backend': 'HerokuServiceTimeBackend',
        'data': 350, // ms
        'success': True,  // assuming it was
    }
    """
    def __init__(self, *args, **kwargs):
        BACKEND_SETTINGS = {
            "HEROKU_APP": None,
            "MEASUREMENT_URL": "/heroku-autoscale/measurement/",
            "MAX_RESPONSE_TIME_IN_SECONDS": 30,
        }
        super(HerokuServiceTimeBackend, self).__init__(*args, **kwargs)
        self.settings = BACKEND_SETTINGS.update(self.settings)
        if self.settings.HEROKU_APP:
            self.heroku_app = self.settings.HEROKU_APP
        else:
            self.heroku_app = self.settings.scaling_backend.heroku_app
        self.url = self.settings.MEASUREMENT_URL
        self.cleaned_url = self.url.replace("http://", "").replace("https://", "")
        if self.cleaned_url[-1] == "/":
            self.cleaned_url = self.cleaned_url[:-1]

    def measure(self, *args, **kwargs):
        success = True
        service_time = 0

        try:
            response = urllib2.urlopen(self.url, None, self.settings.MAX_RESPONSE_TIME_IN_SECONDS)
            assert response.read(1) is not None
        except:  # probably URLError, but anything counts.
            logger.debug("Error getting response from %s." % self.url)
            success = False

        if success:
            line = False
            service_pattern = r'service=([\d]*)ms'
            try:
                for line in self.heroku_app.logs(num=1, tail=True):
                    if self.cleaned_url in line and "service=" in line:
                        matches = re.findall(service_pattern, line)
                        service_time = int(matches[0])
                        success = True
            except:
                pass

        if not success:
            logger.debug("Measurement call not found in logs.")

        return {
            'backend': 'HerokuServiceTimeBackend',
            'data': service_time,
            'success': success
        }
