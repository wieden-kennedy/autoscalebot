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

    @property
    def num_instances(self):
        if not hasattr(self, "_num_instances"):
            self._num_instances = self.get_num_instances()
        return self._num_instances

    def scale_to(self, num_requested, *args, **kwargs):
        raise NotYetImplementedException

    def get_num_instances(self):
        raise NotYetImplementedException
