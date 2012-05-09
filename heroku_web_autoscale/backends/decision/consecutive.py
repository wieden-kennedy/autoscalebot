from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH, NotYetImplementedException
from heroku_web_autoscale.logger import logger
from heroku_web_autoscale.backends.decision.base import BaseDecisionBackend


class ConsecutiveThresholdBackend(BaseDecisionBackend):
    """
    Scales based on a number of consecutive fails or passes exceeding the threshold.
    It expects the following parameters to be provided in the settings:

    NUMBER_OF_FAILS_TO_SCALE_UP_AFTER, which defaults to 3,
    NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER, which defaults to 5,
    MIN_MEASUREMENT_VALUE, which defaults to 400,
    MAX_MEASUREMENT_VALUE, which defaults to 1200,
    MIN_PROCESSES, which defaults to 1,
    MAX_PROCESSES, which defaults to 3,
    INCREMENT, which defaults to 1, and
    POST_SCALE_WAIT_TIME_SECONDS, which defaults to 5,

    It provides a method, get_num_of_processes_to_scale_to that returns
    the number of processes it would like to scale to, as an integer.

    """
    def __init__(self, *args, **kwargs):
        super(ConsecutiveThresholdBackend, self).__init__(*args, **kwargs)
        pass

    @property
    def intepreted_results(self):
        r = []
        for r in self.results:
            if r < self.settings.MIN_MEASUREMENT_VALUE:
                r.append(TOO_LOW)
            elif r > self.settings.MAX_MEASUREMENT_VALUE:
                r.append(TOO_HIGH)
            else:
                r.append(JUST_RIGHT)
        return r

    @property
    def outside_bounds(self):
        return self.current_num_processes > self.max_num_processes or self.current_num_processes < self.min_num_processes

    @property
    def current_num_processes(self):
        return self.autoscalebot.scaling_backend.get_num_processes

    @property
    def needs_scale_up(self):
        return (len(self.intepreted_results) >= self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER and all([h == TOO_HIGH for h in self.intepreted_results[-1 * self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER:]])) or self.outside_bounds

    @property
    def needs_scale_down(self):
        return (len(self.intepreted_results) >= self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER and all([h == TOO_LOW for h in self.intepreted_results[-1 * self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER:]])) or self.outside_bounds

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
        # Check the results, see if scaling is needed.
        if self.outside_bounds:
            return self.nearest_bound
        elif self.needs_scale_up:
            new_num = self.current_num_processes + self.settings.INCREMENT

            if new_num < self.max_num_processes:
                # We have room, scale up.
                return new_num
            else:
                if self.settings.NOTIFY_IF_NEEDS_EXCEED_MAX:
                    # We're already at the max. Notify if enabled.
                    self.notification("notify_needs_above_max")
                return self.max_num_processes

        elif self.needs_scale_down:
            new_num = self.current_num_processes - self.settings.INCREMENT

            if new_num > self.min_num_processes:
                # We have room, scale down.
                return new_num
            else:
                if self.settings.NOTIFY_IF_NEEDS_BELOW_MIN and self.num_dynos > 1:
                    # We're at the min, but could scale down further. Notify if enabled.
                    self.notification("notify_needs_below_min")
                return self.min_num_processes

        return self.current_num_processes
