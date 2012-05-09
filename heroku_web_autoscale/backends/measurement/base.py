from heroku_web_autoscale import NotYetImplementedException
from heroku_web_autoscale.backends import BaseBackend


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

    def measure(self, *args, **kwargs):
        raise NotYetImplementedException
