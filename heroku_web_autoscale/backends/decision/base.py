import datetime
from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH, NotYetImplementedException
from heroku_web_autoscale.logger import logger


class BaseDecisionBackend(object):
    """
    This is the base decision backend.
    """
    def __init__(self, autoscalebot, *args, **kwargs):
        pass

    def setup(self, *args, **kwargs):
        super(BaseDecisionBackend, self).setup(*args, **kwargs)

    def teardown(self, *args, **kwargs):
        super(BaseDecisionBackend, self).teardown(*args, **kwargs)

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

    def _max_num_dynos(self, when=None):
        if not when:
            when = datetime.datetime.now()
        if type(self.settings.MAX_DYNOS) == type({}):
            return self._get_current_value_from_time_dict(self.settings.MAX_DYNOS, when=when)
        else:
            return self.settings.MAX_DYNOS

    def _min_num_dynos(self, when=None):
        if not when:
            when = datetime.datetime.now()
        if type(self.settings.MIN_DYNOS) == type({}):
            return self._get_current_value_from_time_dict(self.settings.MIN_DYNOS, when=when)
        else:
            return self.settings.MIN_DYNOS

    @property
    def _outside_bounds(self):
        return self.num_dynos < self.min_num_dynos() or self.num_dynos > self.max_num_dynos()

    @property
    def _needs_scale_up(self):
        return (len(self.results) >= self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER and all([h == TOO_HIGH for h in self.results[-1 * self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER:]])) or self.outside_bounds

    @property
    def _needs_scale_down(self):
        return (len(self.results) >= self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER and all([h == TOO_LOW for h in self.results[-1 * self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER:]])) or self.outside_bounds

    def _scale_up(self):
        new_dynos = self.num_dynos + self.settings.INCREMENT
        self.heroku_scale(new_dynos)

    def _scale_down(self):
        new_dynos = self.num_dynos - self.settings.INCREMENT
        self.heroku_scale(new_dynos)

    def _scale_to_nearest_bound(self):
        if self.num_dynos > self.max_num_dynos():
            self.heroku_scale(self.max_num_dynos())
        else:
            self.heroku_scale(self.min_num_dynos())

    def _do_autoscale(self):
        """Calls scale up and down, based on need."""
        if self.outside_bounds:
            self.scale_to_nearest_bound()
        elif self.needs_scale_up:
            if self.num_dynos < self.max_num_dynos():
                # We have room, scale up.
                self.scale_up()
            elif self.settings.NOTIFY_IF_NEEDS_EXCEED_MAX:
                # We're already at the min. Notify if enabled.
                self.notification("notify_needs_above_max")

        elif self.needs_scale_down:
            if self.num_dynos > self.min_num_dynos():
                # We have room, scale down.
                self.scale_down()
            elif self.settings.NOTIFY_IF_NEEDS_BELOW_MIN and self.num_dynos > 1:
                # We're at the min, but could scale down further. Notify if enabled.
                self.notification("notify_needs_below_min")

    def get_num_of_processes_to_scale_to(self):
        raise NotYetImplementedException