from heroku_web_autoscale import TOO_LOW, JUST_RIGHT, TOO_HIGH
from heroku_web_autoscale.backends.decision.increment import IncrementBasedDecisionBackend


class ConsecutiveThresholdBackend(IncrementBasedDecisionBackend):
    """
    Scales based on a number of consecutive fails or passes exceeding the threshold.
    It expects the following parameters to be provided in the settings:

    NUMBER_OF_FAILS_TO_SCALE_UP_AFTER, which defaults to 3,
    NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER, which defaults to 5,
    MIN_MEASUREMENT_VALUE, which defaults to 400, and
    MAX_MEASUREMENT_VALUE, which defaults to 1200.

    It provides needs_scale_up and needs_scale_down methods, that
    the IncrementBasedDecisionBackend will use to return the number of
    processes to scale to.

    """
    def __init__(self, *args, **kwargs):
        super(ConsecutiveThresholdBackend, self).__init__(*args, **kwargs)
        pass

    @property
    def _intepreted_results(self):
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
    def needs_scale_up(self):
        return (len(self._intepreted_results) >= self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER and all([h == TOO_HIGH for h in self._intepreted_results[-1 * self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER:]]))

    @property
    def needs_scale_down(self):
        return (len(self._intepreted_results) >= self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER and all([h == TOO_LOW for h in self._intepreted_results[-1 * self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER:]]))
