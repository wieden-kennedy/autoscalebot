from django.core.management.base import BaseCommand
from django.conf import settings as django_settings

from heroku_autoscaler.tasks import start_autoscaler


class Command(BaseCommand):
    help = """Runs the heroku autoscaling heartbeat,
              using django's settings."""

    def handle(self, *args, **options):
        start_autoscaler(settings=django_settings, in_django=True)
