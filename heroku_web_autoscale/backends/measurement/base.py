from heroku_web_autoscale import NotYetImplementedException


class BaseMeasurementBackend(object):
    """
    This is the base measurement class. It should be subclasses to write custom backends.

    The measurement backend is expected to evaluate the load on the app,
    and return a dictionary with the following format:

    {
        'backend': 'BackendClassName',
        'data': "some_data_of_any_type"
    }

    """
    def __init__(self, autoscalebot, *args, **kwargs):
        pass

    def setup(self, *args, **kwargs):
        super(BaseMeasurementBackend, self).setup(*args, **kwargs)

    def teardown(self, *args, **kwargs):
        super(BaseMeasurementBackend, self).teardown(*args, **kwargs)

    def heartbeat_start(self, *args, **kwargs):
        super(BaseMeasurementBackend, self).heartbeat_start(*args, **kwargs)

    def measure(self, *args, **kwargs):
        raise NotYetImplementedException
