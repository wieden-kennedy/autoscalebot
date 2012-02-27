import base64
import urllib
import urllib2
from django.db import models
from heroku_autoscale.conf import settings
from heroku_autoscale import RESPONSE_BUCKET_CHOICES, SCALE_ACTION_CHOICES, MissingParameter


class AutoscaleManager(object):

    @property
    def needs_scale_up(self):
        return all(Heartbeat.objects.all()[:settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER].too_slow)

    @property
    def needs_scale_down(self):
        return all(Heartbeat.objects.all()[:settings.NUMBER_OF_FAILS_TO_SCALE_DOWN_AFTER].too_fast)

    def heroku_scale(self, dynos=None):
        if dynos and settings.HEROKU_APP_NAME and settings.HEROKU_API_KEY:
            url = "https://api.heroku.com/apps/%s/ps/scale" % settings.HEROKU_APP_NAME

            req = urllib2.Request(url=url)
            req.add_header("Accept", "application/json")
            base64string = base64.encodestring(':%s' % settings.HEROKU_API_KEY)[:-1]
            req.add_header("Authorization", "Basic %s" % base64string)
            req.add_data(urllib.urlencode({"qty": dynos, "type": "web"}))

            response = urllib2.urlopen(req)
            try:
                assert int(response.read()) == dynos
            except:
                if settings.NOTIFY_ON_SCALE_FAILS:
                    assert True == "email on scale fails written"

        else:
            # Unhandled raise, because this should never ever be called without all the required settings.
            raise MissingParameter

    @property
    def current_dynos(self):
        if not self._current_dynos:
            self._current_dynos = ScaleHistory.most_recent_scale.num_dynos
        return self._current_dynos

    def scale_up(self):
        new_dynos = self.current_dynos + settings.INCREMENT
        if new_dynos > settings.MAX_DYNOS:
            new_dynos = settings.MAX_DYNOS
        self.heroku_scale(new_dynos)

    def scale_down(self):
        new_dynos = self.current_dynos - settings.INCREMENT
        if new_dynos < settings.MIN_DYNOS:
            new_dynos = settings.MIN_DYNOS
        self.heroku_scale(new_dynos)

    def scale_dynos(self):
        """Calls scale up and down, based on need."""

        if (self.needs_scale_up):
            if self.current_dynos < settings.MAX_DYNOS:
                # We have room, scale up.
                self.scale_up()
            elif settings.NOTIFY_IF_NEEDS_EXCEED_MAX:
                # We're already at the max. Notify if enabled.
                assert True == "the notification email code is written"

        elif (self.needs_scale_down):
            if self.current_dynos > settings.MIN_DYNOS:
                # We have room, scale down.
                self.scale_down()
            elif settings.NOTIFY_IF_NEEDS_EXCEED_MAX and self.current_dynos != 1:
                # We're at the min, but could scale down further. Notify if enabled.
                assert True == "the notification email code is written"


class Heartbeat(models.Model):
    checked_at = models.DateTimeField(editable=False, auto_now_add=True, db_index=True)
    response_time = models.IntegerField(blank=False, null=False)
    response_category = models.CharField(blank=False, null=False, max_width=5, choices=RESPONSE_BUCKET_CHOICES)

    @property
    def too_slow(self):
        return self.response_category == RESPONSE_BUCKET_CHOICES[2][0]

    @property
    def just_right(self):
        return self.response_category == RESPONSE_BUCKET_CHOICES[1][0]

    @property
    def too_fast(self):
        return self.response_category == RESPONSE_BUCKET_CHOICES[0][0]

    class Meta:
        ordering = ("-checked_at")


class ScaleHistory(models.Model):
    action = models.CharField(blank=False, null=False, max_width=5, choices=SCALE_ACTION_CHOICES)
    scaled_at = models.DateTimeField(editable=False, auto_now_add=True, db_index=True)
    num_dynos = models.IntegerField(blank=False, null=False)

    @property
    def most_recent_scale(self):
        return ScaleHistory.objects.all()[0]

    class Meta:
        ordering = ("-scaled_at")


class HeartbeatTestData(models.Model):
    number = models.IntegerField(blank=False, null=False)
