from autoscalebot.backends.notification.base import NotificationBackend


class DjangoEmailBackend(NotificationBackend):

    def send_notification(self, subject="Autoscale-Mail", message=None, *args, **kwargs):
        from django.core.mail import mail_admins
        mail_admins(subject, message, fail_silently=True)

    def notify_scale_diff_too_big(self, *args, **kwargs):
        msg = "Too much scaling over too little time!  We have %s dynos right now." % self.autoscaler.num_dynos
        subject = "Scaled too fast warning"
        self.send_notification(message=msg, subject=subject)
        return msg

    def notify_needs_above_max(self, *args, **kwargs):
        msg = "We are at the max (%s) dynos, but the response is still too slow." % self.autoscaler.num_dynos
        subject = "Demand above max scaling."
        self.send_notification(message=msg, subject=subject)
        return msg

    def notify_needs_below_min(self, *args, **kwargs):
        msg = "We are at the minimum (%s) dynos, but the response is still low enough we could scale down further." % self.autoscaler.num_dynos
        subject = "Load below min scaling."
        self.send_notification(message=msg, subject=subject)
        return msg

    def notify_scale_failed(self, *args, **kwargs):
        subject = "Scale to %s dynos failed." % (self.autoscaler.num_dynos)
        msg = "Just tried to scale, and it failed. We're currently at %s dynos." % self.autoscaler.num_dynos
        self.send_notification(message=msg, subject=subject)
        return msg

    def notify_scaled(self, *args, **kwargs):
        subject = "Scaled to %s dynos" % self.autoscaler.num_dynos
        msg = "Scaled to (%s) dynos." % self.autoscaler.num_dynos
        self.send_notification(message=msg, subject=subject)
        return msg

    def ping_complete(self, time, result, *args, **kwargs):
        """Display the results of a ping"""
        msg = "Ping: %sms, %s" % (time, result)
        subject = msg
        self.send_notification(message=msg, subject=subject)
        return msg
