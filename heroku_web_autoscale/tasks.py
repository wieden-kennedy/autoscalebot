from processing import Process
from heroku_web_autoscale.conf import AutoscaleSettings
from heroku_web_autoscale.models import AutoscaleBot


def _start_bot(bot):
    return bot.bring_to_life()


def start_autoscaler(settings=None, in_django=False):
    settings = AutoscaleSettings(settings=settings, in_django=in_django)

    bots = []
    processes = []
    for process_name, process in settings:
        bots.append(AutoscaleBot(process_name, settings))

    try:
        for bot in bots:
            p = Process(target=_start_bot, args=[bot, ])
            p.start()
            processes.append(p)
    except:
        # Gracefully shut down.
        for bot in bots:
            bot.rest_in_peace()

        for p in processes:
            p.terminate()
