import urllib2
from heroku_web_autoscale.backends.measurement.base import BaseMeasurementBackend
from heroku_web_autoscale.logger import logger
from heroku_web_autoscale import NotYetImplementedException


class ServiceTimeBackend(BaseMeasurementBackend):
    """
    This backend measures the amount of time a url takes to respond.

    It accepts the following parameters:

    heroku_app, which is a heroku app object from the heroku library,
    measurement_url, which defaults to "/heroku-autoscale/measurement/", and
    max_response_time_in_seconds, which defaults to 30.

    It returns a dictionary, with the following format:

    {
        'backend': 'ServiceTimeBackend',
        'data': 350, // ms
        'success': True,  // assuming it was
    }
    """
    def __init__(self, heroku_app, *args, **kwargs):
        super(ServiceTimeBackend, self).__init__(*args, **kwargs)
        self.heroku_app = heroku_app
        self.url = kwargs.get("measurement_url", "/heroku-autoscale/measurement/")
        self.cleaned_url = self.url.replace("http://", "").replace("https://", "")
        if self.cleaned_url[-1] == "/":
            self.cleaned_url = self.cleaned_url[:-1]

        self.max_response_time_in_seconds = kwargs.get("max_response_time_in_seconds", 30)

    def measure(self, *args, **kwargs):
        success = True
        service_time = 0

        try:
            response = urllib2.urlopen(self.url, None, self.max_response_time_in_seconds)
            assert response.read(1) is not None
        except:  # probably URLError, but anything counts.
            logger.debug("Error getting response from %s." % self.url)
            success = False

        if success:
            line = False
            for line in self.heroku_app.logs(num=1, tail=True):
                if self.cleaned_url in line and "service=" in line:
                    print line
                    service_time = line
                    raise NotYetImplementedException
                    success = True
                    break

        if not success:
            logger.debug("Measurement call not found in logs.")

        return {
            'backend': 'ServiceTimeBackend',
            'data': service_time,
            'success': success
        }
