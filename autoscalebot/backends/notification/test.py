from autoscalebot.backends.notification.base import NotificationBackend


class TestBackend(NotificationBackend):

    def __init__(self, *args, **kwargs):
        super(TestBackend, self).__init__(*args, **kwargs)
        self.messages = []

    def send_notification(self, message=None, *args, **kwargs):
        self.messages.append(message)

    def clear_messages(self):
        self.messages = []
