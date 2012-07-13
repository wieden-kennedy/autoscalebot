from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings as django_settings

from autoscalebot.tasks import start_autoscaler


class Command(BaseCommand):
    help = """Runs the autoscalebot heartbeat,
              using django's settings."""

    def handle(self, *args, **options):
        option_list = BaseCommand.option_list[1:] + (
        make_option('-v', '--verbosity', action='store', dest='verbosity', default='4',
            type='choice', choices=map(str, range(5)),
            help='Verbosity level'),
        )
        verbosity = int(options.get('verbosity', 3))
        start_autoscaler(settings=django_settings, in_django=True)
