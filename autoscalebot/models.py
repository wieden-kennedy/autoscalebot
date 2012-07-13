import heroku
import datetime
import time
import urllib2
from autoscalebot import MissingParameter, TOO_LOW, JUST_RIGHT, TOO_HIGH
from autoscalebot.logger import logger


class HerokuAutoscaler(object):

    def __init__(self, settings, *args, **kwargs):
        super(HerokuAutoscaler, self).__init__(*args, **kwargs)
        self.settings = settings
        self.results = []  # List of TOO_LOW, JUST_RIGHT, and TOO_HIGHS
        self.backends = []

        if settings.NOTIFICATION_BACKENDS:
            for b in settings.NOTIFICATION_BACKENDS:
                # Split up the backend and its module
                module_name = b[:b.rfind(".")]
                class_name = b[b.rfind(".") + 1:]
                # Import the module
                m = __import__(module_name, globals(), locals(), [class_name, ])
                # Instantiate the class, passing this autoscaler
                c = getattr(m, class_name)(self)
                # Add it to the list of backends
                self.backends.append(c)

    def notification(self, fn, *args, **kwargs):
        for b in self.backends:
            f = getattr(b, fn)
            f(*args, **kwargs)

    @property
    def heroku_app(self):
        if not hasattr(self, "_heroku_app"):
            cloud = heroku.from_key(self.settings.HEROKU_API_KEY)
            self._heroku_app = cloud.apps[self.settings.HEROKU_APP_NAME]
        return self._heroku_app

    def heroku_scale(self, dynos=None):
        try:
            if dynos and self.settings.HEROKU_APP_NAME and self.settings.HEROKU_API_KEY:
                if dynos < self.min_num_dynos():
                    dynos = self.min_num_dynos()
                if dynos > self.max_num_dynos():
                    dynos = self.max_num_dynos()
                self.heroku_app.processes['web'].scale(dynos)
                self._num_dynos = dynos
                self.notification("notify_scaled")
                self.results = []
            else:
                # Unhandled raise, because this should never ever be called without all the required settings.
                raise MissingParameter
        except:
            self.notification("notify_scale_failed")

    def heroku_get_num_dynos(self):
        return len([1 for i in self.heroku_app.processes['web']])

    @property
    def max_response_time(self):
        return self.settings.MAX_RESPONSE_TIME_IN_MS

    @property
    def min_response_time(self):
        return self.settings.MIN_RESPONSE_TIME_IN_MS

    @property
    def max_response_time_in_seconds(self):
        return self.settings.MAX_RESPONSE_TIME_IN_MS / 1000

    @property
    def min_response_time_in_seconds(self):
        return self.settings.MIN_RESPONSE_TIME_IN_MS / 1000

    def _cmp_time_string(self, a, b):
        a = a[0]
        b = b[0]
        a_hour = int(a[:a.find(":")])
        b_hour = int(b[:b.find(":")])
        if a_hour < b_hour:
            return -1
        elif a_hour > b_hour:
            return 1
        return 0

    def _get_current_value_from_time_dict(self, time_dict, when=None):
            max_dynos = False
            for start_time, max_value in sorted(time_dict.iteritems(), self._cmp_time_string, None, False):
                start_hour = int(start_time[:start_time.find(":")])
                start_minute = int(start_time[start_time.find(":") + 1:])
                if not max_dynos or (when.hour >= start_hour and (when.minute >= start_minute or when.hour > start_hour)):
                    max_dynos = max_value
            return max_dynos

    def max_num_dynos(self, when=None):
        if not when:
            when = datetime.datetime.now()
        if type(self.settings.MAX_DYNOS) == type({}):
            return self._get_current_value_from_time_dict(self.settings.MAX_DYNOS, when=when)
        else:
            return self.settings.MAX_DYNOS

    def min_num_dynos(self, when=None):
        if not when:
            when = datetime.datetime.now()
        if type(self.settings.MIN_DYNOS) == type({}):
            return self._get_current_value_from_time_dict(self.settings.MIN_DYNOS, when=when)
        else:
            return self.settings.MIN_DYNOS

    @property
    def num_dynos(self):
        if not hasattr(self, "_num_dynos"):
            self._num_dynos = self.heroku_get_num_dynos()
        return self._num_dynos

    def add_to_history(self, result):
        self.results.append(result)

        # Trim history.
        if self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER > self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER:
            if len(self.results) > self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER:
                self.results = self.results[-1 * self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER:]
        else:
            if len(self.results) > self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER:
                self.results = self.results[-1 * self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER:]

    @property
    def outside_bounds(self):
        return self.num_dynos < self.min_num_dynos() or self.num_dynos > self.max_num_dynos()

    @property
    def needs_scale_up(self):
        return (len(self.results) >= self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER and all([h == TOO_HIGH for h in self.results[-1 * self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER:]])) or self.outside_bounds

    @property
    def needs_scale_down(self):
        return (len(self.results) >= self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER and all([h == TOO_LOW for h in self.results[-1 * self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER:]])) or self.outside_bounds

    def scale_up(self):
        new_dynos = self.num_dynos + self.settings.INCREMENT
        self.heroku_scale(new_dynos)

    def scale_down(self):
        new_dynos = self.num_dynos - self.settings.INCREMENT
        self.heroku_scale(new_dynos)

    def scale_to_nearest_bound(self):
        if self.num_dynos > self.max_num_dynos():
            self.heroku_scale(self.max_num_dynos())
        else:
            self.heroku_scale(self.min_num_dynos())

    def do_autoscale(self):
        """Calls scale up and down, based on need."""
        if self.outside_bounds:
            self.scale_to_nearest_bound()
        elif self.needs_scale_up:
            if self.num_dynos < self.max_num_dynos():
                # We have room, scale up.
                self.scale_up()
            elif self.settings.NOTIFY_IF_NEEDS_EXCEED_MAX:
                # We're already at the min. Notify if enabled.
                self.notification("notify_needs_above_max")

        elif self.needs_scale_down:
            if self.num_dynos > self.min_num_dynos():
                # We have room, scale down.
                self.scale_down()
            elif self.settings.NOTIFY_IF_NEEDS_BELOW_MIN and self.num_dynos > 1:
                # We're at the min, but could scale down further. Notify if enabled.
                self.notification("notify_needs_below_min")

    def ping_and_store(self):
        """Pings the url, records the response time, and stores the results."""
        start_time = time.time()
        errored_out = False

        try:
            response = urllib2.urlopen(self.settings.HEARTBEAT_URL, None, self.max_response_time_in_seconds)
            assert response.read(1) is not None
        except:  # probably URLError, but anything counts.
            errored_out = True
        end_time = time.time()

        diff = end_time - start_time
        diff = diff * 1000
        logger.debug("Response time: %sms." % diff)

        if diff > self.max_response_time or errored_out:
            result = TOO_HIGH
        elif diff < self.min_response_time:
            result = TOO_LOW
        else:
            result = JUST_RIGHT

        self.add_to_history(result)
        if self.settings.NOTIFY_ON_EVERY_PING:
            self.notification("ping_complete", diff, result)

        return diff

    def full_heartbeat(self):
        heartbeat_time = self.ping_and_store()
        self.do_autoscale()
        return heartbeat_time

try:
    from django.db import models

    class HeartbeatTestData(models.Model):
        number = models.IntegerField(blank=False, null=False)

except:
    pass
