import sys
import optparse

from heroku_autoscaler.tasks import start_heartbeat
from heroku_autoscaler import version


def main(args=sys.argv[1:]):

    parser = optparse.OptionParser(
        usage="%prog or type %prog -h (--help) for help",
        version=version
    )

    parser.add_option("--settings",
                      dest="settings",
                      default=None,
                      type="string",
                      help='settings to use when autoscaling')

    options, args = parser.parse_args()

    if options.settings:
        settings = __import__(options.settings)

    start_heartbeat(settings=settings)
