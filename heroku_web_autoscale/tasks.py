from heroku_web_autoscale.conf import AutoscaleSettings
from heroku_web_autoscale.models import AutoscaleBot


def start_autoscaler(settings=None, in_django=False):
    settings = AutoscaleSettings(settings=settings, in_django=in_django)

    bots = []
    for process_name, process in settings:
        bots.append(AutoscaleBot(process_name, settings))

    try:
        for bot in bots:
            bot.bring_to_life()
    except:
        for bot in bots:
            bot.rest_in_peace()
