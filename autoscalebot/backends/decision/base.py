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

    MIN_PROCESSES, which defaults to 1,
    MAX_PROCESSES, which defaults to 3,
    INCREMENT, which defaults to 1,
    POST_SCALE_WAIT_TIME_SECONDS, which defaults to 5, and
    HISTORY_LENGTH, which defaults to 10.

    It returns an integer.

    """

    def __init__(self, *args, **kwargs):
        DEFAULT_SETTINGS = {
            "MIN_PROCESSES": 1,
            "MAX_PROCESSES": 3,
            "INCREMENT": 1,
            "POST_SCALE_WAIT_TIME_SECONDS": 5,
            "HISTORY_LENGTH": 10
        }
        super(BaseDecisionBackend, self).__init__(*args, **kwargs)
        self.settings = DEFAULT_SETTINGS.update(self.autoscalebot.settings.DECISION)
        self.results = self.autoscalebot.results

    def _cmp_time_string(self, a, b):
        a = a[0]
        b = b[0]
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
