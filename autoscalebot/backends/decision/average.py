from autoscalebot.backends.decision.increment import IncrementBasedDecisionBackend


class AverageThresholdBackend(IncrementBasedDecisionBackend):
    """
    Scales based on a number of consecutive fails or passes exceeding the threshold.
    It expects the following parameters to be provided in the settings:

    NUMBER_OF_MEASUREMENTS_TO_AVERAGE, which defaults to 3,
    MIN_MEASUREMENT_VALUE, which defaults to 0, and
    MAX_MEASUREMENT_VALUE, which defaults to 20.

    It provides needs_scale_up and needs_scale_down methods, that
    the IncrementBasedDecisionBackend will use to return the number of
    processes to scale to.

    """
    def __init__(self, *args, **kwargs):
        BACKEND_SETTINGS = {
            "NUMBER_OF_MEASUREMENTS_TO_AVERAGE": 3,
            "MIN_MEASUREMENT_VALUE": 0,
            "MAX_MEASUREMENT_VALUE": 20,
        }
        super(AverageThresholdBackend, self).__init__(*args, **kwargs)
        self.settings = BACKEND_SETTINGS.update(self.settings)

    def heartbeat_start(self, *args, **kwargs):
        super(AverageThresholdBackend, self).heartbeat_start(*args, **kwargs)
        self.__average_measurement = None

    @property
    def _average_measurement(self):
        if not hasattr(self, "__average_measurement") or self.__average_measurement is None:
            self.__average_measurement = sum(self.results[:self.settings.NUMBER_OF_MEASUREMENTS_TO_AVERAGE]) / len(self.results[:self.settings.NUMBER_OF_MEASUREMENTS_TO_AVERAGE])
        return self.__average_measurement

    @property
    def _meets_minimum_measurements(self):
        return len(self.results) >= self.settings.NUMBER_OF_MEASUREMENTS_TO_AVERAGE

    @property
    def needs_scale_up(self):
        if not self._meets_minimum_measurements:
            return self.current_num_processes
        else:
            return self._average_measurement > self.settings.MAX_MEASUREMENT_VALUE

    @property
    def needs_scale_down(self):
        if not self._meets_minimum_measurements:
            return self.current_num_processes
        else:
            return self._average_measurement < self.settings.MIN_MEASUREMENT_VALUE
