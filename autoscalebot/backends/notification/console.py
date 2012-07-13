from autoscalebot.backends.notification.base import NotificationBackend


class ConsoleBackend(NotificationBackend):

    def send_notification(self, message=None, *args, **kwargs):
        print(message)

    def ping_complete(self, time, result, *args, **kwargs):
        msg = "Ping: %sms, %s" % (time, result)
        self.send_notification(message=msg)
        return msg
