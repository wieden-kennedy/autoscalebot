import datetime
from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH, NotYetImplementedException
from heroku_web_autoscale.logger import logger


class BaseDecisionBackend(object):
    """
    This is the base decision backend.
    """
    def __init__(self, autoscalebot, *args, **kwargs):
        self.autoscalebot = autoscalebot
        self.settings = self.autoscalebot.settings.DECISION
        self.results = self.autoscalebot.results

    def setup(self, *args, **kwargs):
        super(BaseDecisionBackend, self).setup(*args, **kwargs)

    def teardown(self, *args, **kwargs):
        super(BaseDecisionBackend, self).teardown(*args, **kwargs)

    def heartbeat_start(self, *args, **kwargs):
        super(BaseDecisionBackend, self).heartbeat_start(*args, **kwargs)

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

    def get_num_of_processes_to_scale_to(self):
        raise NotYetImplementedException
