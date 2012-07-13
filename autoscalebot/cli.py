import optparse
from os import curdir
from os.path import abspath
import sys

from autoscalebot.tasks import start_autoscaler
from autoscalebot import version


def main(args=sys.argv[1:]):
    CLI_ROOT = abspath(curdir)
    sys.path.insert(0, CLI_ROOT)

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

    start_autoscaler(settings=settings)
