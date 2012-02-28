import time
import heroku
import urllib2
from heroku_autoscaler import MissingParameter, TOO_LOW, JUST_RIGHT, TOO_HIGH


class HerokuAutoscaler(object):

    def __init__(self, settings, *args, **kwargs):
        super(HerokuAutoscaler, self).__init__(*args, **kwargs)
        self.settings = settings
        self.results = []  # List of TOO_LOW, JUST_RIGHT, and TOO_HIGHS

    @property
    def heroku_app(self):
        if not hasattr(self, "_heroku_app"):
            cloud = heroku.from_key(self.settings.HEROKU_API_KEY)
            self._heroku_app = cloud.apps[self.settings.HEROKU_APP_NAME]
        return self._heroku_app

    def heroku_scale(self, dynos=None):
        if dynos and self.settings.HEROKU_APP_NAME and self.settings.HEROKU_API_KEY:
            self.heroku_app.processes['web'].scale(dynos)
            self._num_dynos = dynos

        else:
            # Unhandled raise, because this should never ever be called without all the required settings.
            raise MissingParameter

    def heroku_get_num_dynos(self):
        return len([1 for i in self.heroku_app.processes['web']])

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
    def needs_scale_up(self):
        return len(self.results) >= self.settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER and all([h == TOO_HIGH for h in self.results])

    @property
    def needs_scale_down(self):
        return len(self.results) >= self.settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER and all([h == TOO_LOW for h in self.results])

    def scale_up(self):
        new_dynos = self.num_dynos + self.settings.INCREMENT
        if new_dynos > self.settings.MAX_DYNOS:
            new_dynos = self.settings.MAX_DYNOS
        self.heroku_scale(new_dynos)

    def scale_down(self):
        new_dynos = self.num_dynos - self.settings.INCREMENT
        if new_dynos < self.settings.MIN_DYNOS:
            new_dynos = self.settings.MIN_DYNOS
        self.heroku_scale(new_dynos)

    def do_autoscale(self):
        """Calls scale up and down, based on need."""
        if self.needs_scale_up:
            if self.num_dynos < self.settings.MAX_DYNOS:
                # We have room, scale up.
                self.scale_up()
            elif self.settings.NOTIFY_IF_NEEDS_EXCEED_MAX:
                # We're already at the max. Notify if enabled.
                assert True == "the notification email code is written"

        elif self.needs_scale_down:
            if self.num_dynos > self.settings.MIN_DYNOS:
                # We have room, scale down.
                self.scale_down()
            elif self.settings.NOTIFY_IF_NEEDS_BELOW_MIN and self.num_dynos != 1:
                # We're at the min, but could scale down further. Notify if enabled.
                assert True == "the notification email code is written"

    def ping_and_store(self):
        """Pings the url, records the response time, and stores the results."""
        start_time = time.time()
        req = urllib2.Request(url=self.settings.HEARTBEAT_URL)
        errored_out = False
        response = urllib2.urlopen(req)
        try:
            assert response.read(1) is not None
        except:
            errored_out = True
        end_time = time.time()

        diff = end_time - start_time
        diff = diff * 1000

        if diff > self.settings.MAX_RESPONSE_TIME_IN_MS or errored_out:
            result = TOO_HIGH
        elif diff < self.settings.MIN_RESPONSE_TIME_IN_MS:
            result = TOO_LOW
        else:
            result = JUST_RIGHT

        self.add_to_history(result)

    def full_heartbeat(self):
        self.ping_and_store()
        self.do_autoscale()

try:
    from django.db import models

    class HeartbeatTestData(models.Model):
        number = models.IntegerField(blank=False, null=False)

except:
    pass
