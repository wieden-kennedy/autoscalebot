from heroku_web_autoscale.backends.notification.base import NotificationBackend


class DjangoEmailBackend(NotificationBackend):

    def send_notification(self, message=None, subject=None, *args, **kwargs):
        from django.core.mail import mail_admins
        mail_admins("Autoscale-Mail", message)
