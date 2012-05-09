from heroku_web_autoscale import NotYetImplementedException
from heroku_web_autoscale.backends.decision.base import BaseDecisionBackend


class IncrementBasedDecisionBackend(BaseDecisionBackend):
    """
    This is the a subclass of the base decision backend, designed around the
    following logic:

    Subclasses will implement needs_scale_up and needs_scale_down methods.

    Based on the results of those method calls, the backend will scale up,
    scale down, or stay steady.  Scaling changes happen as a function of the
    INCREMENT setting, and stay within the max and min bounds.
    """

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

    @property
    def needs_scale_up(self):
        raise NotYetImplementedException

    @property
    def needs_scale_down(self):
        raise NotYetImplementedException
