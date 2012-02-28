from django.core.management.base import BaseCommand

from heroku_autoscaler.tasks import start_heartbeat


class Command(BaseCommand):
    help = """Runs the heroku autoscaling heartbeat,
              using django's settings."""

    def handle(self, *args, **options):
        start_heartbeat()
