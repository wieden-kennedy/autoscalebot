from django.db import models


class AutoscaleBeat(models.Model):
    pass


class AutoscaleHeartbeatTestData(models.Model):
    number = models.IntegerField(blank=False, null=False)
