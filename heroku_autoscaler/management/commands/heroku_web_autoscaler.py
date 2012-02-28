from django.core.management.base import BaseCommand

from heroku_autoscale.tasks import start_heartbeat


class Command(BaseCommand):
    help = 'Runs the heroku autoscaling heartbeat'

    def handle(self, *args, **options):
        start_heartbeat()
