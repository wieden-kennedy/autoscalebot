class AutoscaleSettings:

    def _set_attr_from_settings(self, key_name, default=None):
        setattr(self, key_name, getattr(self.settings, "%s%s" % (self.prefix, key_name), default))

    def initialize_settings(self):
        for k, v in self.SETTINGS_AND_DEFAULTS.iteritems():
            self._set_attr_from_settings(k, v)

    def __init__(self, settings=None, in_django=False):
        self.in_django = in_django
        self.prefix = ""
        if self.in_django:
            self.prefix = "AUTOSCALE_"
        self.settings = settings

        self.SETTINGS_AND_DEFAULTS = {
            "HEROKU_APP_NAME": None,
            "HEROKU_API_KEY": None,
            "HEARTBEAT_INTERVAL_IN_SECONDS": 30,
            "HEARTBEAT_URL": "/autoscalebot/heartbeat/v1",
            "MAX_RESPONSE_TIME_IN_MS": 1000,
            "MIN_RESPONSE_TIME_IN_MS": 200,
            "NUMBER_OF_FAILS_TO_SCALE_UP_AFTER": 3,
            "NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER": 5,
            "MAX_DYNOS": 3,
            "MIN_DYNOS": 1,
            "INCREMENT": 1,
            "NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD": None,
            "NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES": None,
            "NOTIFY_IF_NEEDS_EXCEED_MAX": True,
            "NOTIFY_IF_NEEDS_BELOW_MIN": False,
            "NOTIFY_ON_EVERY_PING": False,
            "NOTIFY_ON_SCALE_FAILS": False,
            "NOTIFICATION_BACKENDS": [],
        }

        self.initialize_settings()
