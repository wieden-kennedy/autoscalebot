class AutoscaleSettings:
    def __init__(self, settings=None, in_django=False):
        prefix = ""
        if in_django:
            prefix = "AUTOSCALE_"

        self.HEROKU_APP_NAME = getattr(settings, "%sHEROKU_APP_NAME" % prefix, None)
        self.HEROKU_API_KEY = getattr(settings, "%sHEROKU_API_KEY" % prefix, None)
        self.HEARTBEAT_INTERVAL_IN_SECONDS = getattr(settings, "%sHEARTBEAT_INTERVAL_IN_SECONDS" % prefix, 30)
        self.HEARTBEAT_URL = getattr(settings, "%sHEARTBEAT_URL" % prefix, "/heroku-autoscale/heartbeat/v1")
        self.MAX_RESPONSE_TIME_IN_MS = getattr(settings, "%sMAX_RESPONSE_TIME_IN_MS" % prefix, 1000)
        self.MIN_RESPONSE_TIME_IN_MS = getattr(settings, "%sMIN_RESPONSE_TIME_IN_MS" % prefix, 200)
        self.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER = getattr(settings, "%sNUMBER_OF_FAILS_TO_SCALE_UP_AFTER" % prefix, 3)
        self.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER = getattr(settings, "%sNUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER" % prefix, 5)
        self.MAX_DYNOS = getattr(settings, "%sMAX_DYNOS" % prefix, 3)
        self.MIN_DYNOS = getattr(settings, "%sMIN_DYNOS" % prefix, 1)
        self.INCREMENT = getattr(settings, "%sINCREMENT" % prefix, 1)
        self.NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD = getattr(settings, "%sNOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD" % prefix, None)
        self.NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES = getattr(settings, "%sNOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES" % prefix, None)
        self.NOTIFY_IF_NEEDS_EXCEED_MAX = getattr(settings, "%sNOTIFY_IF_NEEDS_EXCEED_MAX" % prefix, True)
        self.NOTIFY_IF_NEEDS_BELOW_MIN = getattr(settings, "%sNOTIFY_IF_NEEDS_BELOW_MIN" % prefix, False)
        self.NOTIFY_ON_SCALE_FAILS = getattr(settings, "%sNOTIFY_ON_SCALE_FAILS" % prefix, False)
