import base64
import urllib, urllib2
from django.db import models
from django.conf import settings
from heroku_autoscale import RESPONSE_BUCKET_CHOICES, SCALE_ACTION_CHOICES, MissingParameter


class Autoscale(object):

    @classmethod
    def needs_scale_up():
        return all(Heartbeat.objects.all()[:settings.AUTOSCALE_NUMBER_OF_FAILS_TO_SCALE_UP_AFTER].too_slow)

    @classmethod
    def needs_scale_down():
        return all(Heartbeat.objects.all()[:settings.AUTOSCALE_NUMBER_OF_FAILS_TO_SCALE_DOWN_AFTER].too_fast)

    @classmethod
    def heroku_scale(dynos=None):
        if dynos and settings.AUTOSCALE_HEROKU_APP_NAME and settings.AUTOSCALE_HEROKU_API_KEY:
            url = "https://api.heroku.com/apps/%s/ps/scale" % settings.AUTOSCALE_HEROKU_APP_NAME

            req = urllib2.Request(url=url)
            req.add_header("Accept", "application/json")
            base64string = base64.encodestring(':%s' % settings.AUTOSCALE_HEROKU_API_KEY)[:-1]
            req.add_header("Authorization", "Basic %s" % base64string)
            req.add_data(urllib.urlencode({"qty": dynos, "type": "web"}))

            response = urllib2.urlopen(req)
            assert int(response.read()) == dynos

        else:
            raise MissingParameter


class Heartbeat(models.Model):
    when = models.DateTimeField(editable=False, auto_now_add=True)
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


class ScaleHistory(models.Model):
    action = models.CharField(blank=False, null=False, max_width=5, choices=SCALE_ACTION_CHOICES)
    when = models.DateTimeField(editable=False, auto_now_add=True)
    num_dynos = models.IntegerField(blank=False, null=False)


class HeartbeatTestData(models.Model):
    number = models.IntegerField(blank=False, null=False)
