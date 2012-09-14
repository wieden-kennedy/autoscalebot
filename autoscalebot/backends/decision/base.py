import datetime
from autoscalebot import NotYetImplementedException
from autoscalebot.backends import BaseBackend


class BaseDecisionBackend(BaseBackend):
    """
    This is the base decision backend. Subclasses are expected to implement a
    get_num_of_processes_to_scale_to method that returns an integer of the number
    of processes desired.

    The backend is responsible for making sense of the results, deciding what value
    is needed, and making sure that value falls within the specified max and min caps.

    If no change is needed, or an error occurs, the backend is expected to return the
    current number of processes.

    It uses the following settings:

    min_processes, which defaults to 1,
    max_processes, which defaults to 3,
    increment, which defaults to 1,
    post_scale_delay_seconds, which defaults to 0, and

    """

    def __init__(self, *args, **kwargs):
        super(BaseDecisionBackend, self).__init__(*args, **kwargs)
        self.results = self.autoscalebot.results

    @property
    def settings(self):
        return self.autoscalebot.settings.DECISION.SETTINGS

    def default_settings(self):
        return {
            "min_processes": 1,
            "max_processes": 3,
            "increment": 1,
            "post_scale_delay_seconds": 0
        }

    def _cmp_time_string(self, a, b):
        """
        Compares two times, of format 5:30 or 17:00.
        Returns -1 if b is later than a,
                 1 if a is later than b, and
                 0 if the times are the same.
        """
        a = a.replace(":", "")
        b = b.replace(":", "")
        a_hour = int(a[:a.find(":")])
        b_hour = int(b[:b.find(":")])
        if a_hour < b_hour:
            return -1
        elif a_hour > b_hour:
            return 1
        return 0

    def _get_current_value_from_time_dict(self, time_dict, when=None):
            max_dynos = False
            for start_time, max_value in sorted(time_dict.iteritems(), self._cmp_time_string, None, False):
                start_hour = int(start_time[:start_time.find(":")])
                start_minute = int(start_time[start_time.find(":") + 1:])
                if not max_dynos or (when.hour >= start_hour and (when.minute >= start_minute or when.hour > start_hour)):
                    max_dynos = max_value
            return max_dynos

    @property
    def max_num_processes(self, when=None):
        if not when:
            when = datetime.datetime.now()
        if type(self.settings.MAX_PROCESSES) == type({}):
            return self._get_current_value_from_time_dict(self.settings.MAX_PROCESSES, when=when)
        else:
            return self.settings.MAX_PROCESSES

    @property
    def min_num_processes(self, when=None):
        if not when:
            when = datetime.datetime.now()
        if type(self.settings.MIN_PROCESSES) == type({}):
            return self._get_current_value_from_time_dict(self.settings.MIN_PROCESSES, when=when)
        else:
            return self.settings.MIN_PROCESSES

    @property
    def outside_bounds(self):
        return self.current_num_processes > self.max_num_processes or self.current_num_processes < self.min_num_processes

    @property
    def current_num_processes(self):
        return self.autoscalebot.scaling_backend.get_num_processes

    @property
    def nearest_bound(self):
        n = self.current_num_processes
        if n > self.max_num_processes:
            return self.max_num_processes
        elif n < self.min_num_processes:
            return self.min_num_processes
        else:
            if self.max_num_processes - n > n - self.min_num_processes:
                return self.min_num_processes
            else:
                return self.max_num_processes

    def get_num_of_processes_to_scale_to(self):
        raise NotYetImplementedException
