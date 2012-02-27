from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs the heroku autoscaling heartbeat'

    def handle(self, *args, **options):
        from heroku_autoscale.tasks import start_heartbeat
        from heroku_autoscale.conf import settings

        start_heartbeat(settings=settings)
