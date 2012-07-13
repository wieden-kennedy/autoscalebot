from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from autoscalebot.tests import *


class TestScalingBackend:

    def setUp(self):
        self.test_scaler


class TestScalingBaseBackend(TestScalingBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestScalingHerokuBackend(TestScalingBackend):

    def tests_written(self):
        assert_equals(True, "Test written")
