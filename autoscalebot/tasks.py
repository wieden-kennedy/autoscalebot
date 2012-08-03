from processing import Process
from autoscalebot.conf import AutoscaleSettings
from autoscalebot.models import AutoscaleBot


def _start_bot(bot):
    return bot.setup()


def start_autoscaler(settings=None, in_django=False):
    settings = AutoscaleSettings(settings=settings, in_django=in_django)

    bots = []
    processes = []
    for nickname, process_settings in settings:
        bots.append(AutoscaleBot(nickname, process_settings))

    try:
        for bot in bots:
            p = Process(target=_start_bot, args=[bot, ])
            p.start()
            processes.append(p)
    except:
        # Gracefully shut down.
        for bot in bots:
            bot.teardown()

        for p in processes:
            p.terminate()
