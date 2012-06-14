from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from heroku_web_autoscale.tests import *


class TestMeasurementBackend:

    def setUp(self):
        self.test_scaler


class TestMeasurementBaseBackend(TestMeasurementBackend):

    def test_measurement_is_accurate(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")


class TestMeasurementAppBackend(TestMeasurementBackend):

    def test_measurement_is_accurate(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")


class TestMeasurementCeleryBackend(TestMeasurementBackend):

    def test_measurement_is_accurate(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")


class TestMeasurementResponsetimeBackend(TestMeasurementBackend):

    def test_measurement_is_accurate(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")


class TestMeasurementServicetimeHerokuBackend(TestMeasurementBackend):

    def test_measurement_is_accurate(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")
