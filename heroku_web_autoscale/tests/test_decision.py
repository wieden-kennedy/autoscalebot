from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from heroku_web_autoscale.tests import *


class TestDecisionBackend:

    def setUp(self):
        self.test_scaler


class TestDecsionBaseBackend(TestDecisionBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestDecsionIncrementBackend(TestDecisionBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestDecsionAverageBackend(TestDecisionBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestDecsionConsecutiveBackend(TestDecisionBackend):

    def tests_written(self):
        assert_equals(True, "Test written")
