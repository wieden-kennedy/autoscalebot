from heroku_web_autoscale.backends.notification.base import NotificationBackend


class ConsoleBackend(NotificationBackend):

    def send_notification(self, message=None, *args, **kwargs):
        print(message)
