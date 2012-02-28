try:
    from django.conf import settings as django_settings
    assert hasattr(django_settings, "HEROKU_APP_NAME") and hasattr(django_settings, "HEROKU_API_KEY")
except:
    django_settings = {}


class SettingsObj:
    pass

settings = SettingsObj()

settings.HEROKU_APP_NAME = getattr(django_settings, "AUTOSCALE_HEROKU_APP_NAME", None)
settings.HEROKU_API_KEY = getattr(django_settings, "AUTOSCALE_HEROKU_API_KEY", None)
settings.HEARTBEAT_INTERVAL_IN_SECONDS = getattr(django_settings, "AUTOSCALE_HEARTBEAT_INTERVAL_IN_SECONDS", 30)
settings.HEARTBEAT_URL = getattr(django_settings, "AUTOSCALE_HEARTBEAT_URL", '/heroku-autoscale/heartbeat/v1')
settings.MAX_RESPONSE_TIME_IN_MS = getattr(django_settings, "AUTOSCALE_MAX_RESPONSE_TIME_IN_MS", 1000)
settings.MIN_RESPONSE_TIME_IN_MS = getattr(django_settings, "AUTOSCALE_MIN_RESPONSE_TIME_IN_MS", 200)
settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER = getattr(django_settings, "AUTOSCALE_NUMBER_OF_FAILS_TO_SCALE_UP_AFTER", 3)
settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER = getattr(django_settings, "AUTOSCALE_NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER", 5)
settings.MAX_DYNOS = getattr(django_settings, "AUTOSCALE_MAX_DYNOS", 3)
settings.MIN_DYNOS = getattr(django_settings, "AUTOSCALE_MIN_DYNOS", 1)
settings.INCREMENT = getattr(django_settings, "AUTOSCALE_INCREMENT", 1)
settings.NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD = getattr(django_settings, "AUTOSCALE_NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD", None)
settings.NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES = getattr(django_settings, "AUTOSCALE_NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES", None)
settings.NOTIFY_IF_NEEDS_EXCEED_MAX = getattr(django_settings, "AUTOSCALE_NOTIFY_IF_NEEDS_EXCEED_MAX", True)
settings.NOTIFY_IF_NEEDS_BELOW_MIN = getattr(django_settings, "AUTOSCALE_NOTIFY_IF_NEEDS_BELOW_MIN", False)
settings.NOTIFY_ON_SCALE_FAILS = getattr(django_settings, "AUTOSCALE_NOTIFY_ON_SCALE_FAILS", False)

try:
    from autoscale_settings import settings as custom_autoscale_settings
    for k, v in custom_autoscale_settings.iteritems():
        setattr(settings, k, v)
except:
    pass
