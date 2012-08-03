from autoscalebot.util import Struct


class BaseBackend(object):

    def __init__(self, autoscalebot, *args, **kwargs):
        # Backends can provide:
        # self.DEFAULT_BACKEND_SETTINGS
        # self.DEFAULT_BASE_SETTINGS
        # Both will be pulled as defaults into the master bot settings.
        self.autoscalebot = autoscalebot

    def add_default_settings_from_dict(self, settings, defaults):
        defaults.update(settings.__dict__)
        return Struct(defaults)
