from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Runs the heroku autoscaling heartbeat'

    def handle(self, *args, **options):
        from heroku_autoscale