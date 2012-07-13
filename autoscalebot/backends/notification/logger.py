import logging
from autoscalebot.backends.notification.base import NotificationBackend

logger = logging.getLogger("autoscalebot.LoggerBackend")


class LoggerBackend(NotificationBackend):

    def send_notification(self, message=None, log_level="INFO", *args, **kwargs):
        logger.log(log_level, message)
