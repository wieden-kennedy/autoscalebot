from heroku_web_autoscale import NotYetImplementedException


class BaseScalingBackend(object):
    """
    This is the base scaling class
    """
    def __init__(self, autoscalebot, *args, **kwargs):
        self.autoscalebot = autoscalebot

    def setup(self, *args, **kwargs):
        super(BaseScalingBackend, self).setup(*args, **kwargs)

    def teardown(self, *args, **kwargs):
        super(BaseScalingBackend, self).teardown(*args, **kwargs)

    def heartbeat_start(self, *args, **kwargs):
        super(BaseScalingBackend, self).heartbeat_start(*args, **kwargs)

    @property
    def num_processes(self):
        if not hasattr(self, "_num_processes"):
            self._num_processes = self.get_num_processes()
        return self._num_processes

    def scale_to(self, num_requested, *args, **kwargs):
        raise NotYetImplementedException

    def get_num_processes(self):
        raise NotYetImplementedException
