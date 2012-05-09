from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from heroku_web_autoscale.tests import *


class TestMeasurementBackend:

    def setUp(self):
        self.test_scaler


class TestMeasurementBaseBackend(TestMeasurementBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestMeasurementAppBackend(TestMeasurementBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestMeasurementCeleryBackend(TestMeasurementBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestMeasurementResponsetimeBackend(TestMeasurementBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestMeasurementServicetimeHerokuBackend(TestMeasurementBackend):

    def tests_written(self):
        assert_equals(True, "Test written")
