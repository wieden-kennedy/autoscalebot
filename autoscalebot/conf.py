from autoscalebot.util import Struct


class AutoscaleSettings:

    def __init__(self, settings=None, in_django=False):
        self.in_django = in_django
        self.settings_dict = settings

        self.DEFAULT_SETTINGS = {
            'MEASUREMENT': {
                'BACKEND': 'autoscalebot.backends.measurement.ResponseTimeBackend',
                'SETTINGS': {}
            },
            'DECISION': {
                'BACKEND': 'autoscalebot.backends.decision.ConsecutiveThresholdBackend',
                'SETTINGS': {}
            },
            'SCALING': {
                'BACKEND': 'autoscalebot.backends.scaling.HerokuBackend',
                'SETTINGS': {}
            },
            'NOTIFICATION': {
                'BACKENDS': [
                    'autoscalebot.backends.notification.ConsoleBackend',
                ],
                'SETTINGS': {
                    'NOTIFY_ON': ["SCALE", "BELOW_MIN", "ABOVE_MAX"],
                },
            }
        }
        settings_with_defaults = self.DEFAULT_SETTINGS
        settings_with_defaults.update(self.settings_dict)
        converted_settings = Struct(settings_with_defaults)
        self.__dict__.update(converted_settings.__dict__)

    def update(self, d):
        new_dict = self.__dict__
        new_dict.update(d)
        self.__dict__.update(d)
