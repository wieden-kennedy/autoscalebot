class NotImplementedError(Exception):
    pass


class NotificationBackend(object):

    def __init__(self, autoscaler, *args, **kwargs):
        """Sets the autoscaler object, to be used in notifications"""
        self.autoscaler = autoscaler

    def send_notification(self, message=None, *args, **kwargs):
        """Send the notification.  By default, you'll have a message."""
        raise NotImplementedError

    def notify_scale_diff_too_big(self, *args, **kwargs):
        """Notification for when the the number of scales over a time period exceeds allowed amount"""

        msg = "Too much scaling over too little time!  We have %s dynos right now." % self.autoscaler.num_dynos
        self.send_notification(message=msg)
        return msg

    def notify_needs_above_max(self, *args, **kwargs):
        """Notification for when we are at the max dynos, and the responses are still too slow."""

        msg = "We are at the max (%s) dynos, but the response is still too slow." % self.autoscaler.num_dynos
        self.send_notification(message=msg)
        return msg

    def notify_needs_below_min(self, *args, **kwargs):
        """Notification for when we are at the min dynos, but the response is still below the scale down threshold"""

        msg = "We are at the minimum (%s) dynos, but the response is still low enough we could scale down further." % self.autoscaler.num_dynos
        self.send_notification(message=msg)
        return msg

    def notify_scale_failed(self, *args, **kwargs):
        """Notification that scaling failed."""

        msg = "Just tried to scale, and it failed. We're currently at %s dynos." % self.autoscaler.num_dynos
        self.send_notification(message=msg)
        return msg

    def notify_scaled(self, *args, **kwargs):
        """Notification that scaling happened"""

        msg = "Scaled to (%s) dynos." % self.autoscaler.num_dynos
        self.send_notification(message=msg)
        return msg

    def ping_complete(self, time, result, *args, **kwargs):
        """Display the results of a ping"""

        msg = "Ping: %sms, %s" % (time, result)
        # self.send_notification(message=msg)
        return msg
