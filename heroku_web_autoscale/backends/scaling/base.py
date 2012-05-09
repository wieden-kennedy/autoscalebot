from heroku_web_autoscale import NotYetImplementedException
from heroku_web_autoscale.backends import BaseBackend


class BaseScalingBackend(BaseBackend):
    """
    This is the base scaling class.

    Subclasses are expected to implement get_num_processes and
    scale_to methods.

    """

    @property
    def num_processes(self):
        if not hasattr(self, "_num_processes"):
            self._num_processes = self.get_num_processes()
        return self._num_processes

    def scale_to(self, num_requested, *args, **kwargs):
        raise NotYetImplementedException

    def get_num_processes(self):
        raise NotYetImplementedException
