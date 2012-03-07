import logging
from heroku_web_autoscale.backends.notification.base import NotificationBackend

logger = logging.getLogger("heroku_web_autoscale.LoggerBackend")


class LoggerBackend(NotificationBackend):

    def send_notification(self, message=None, log_level="INFO", *args, **kwargs):
        logger.log(log_level, message)
