from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from heroku_web_autoscale.tests import *


class TestNotificationBackend:

    def setUp(self):
        self.test_scaler


class TestNotificationBaseBackend(TestNotificationBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestNotificationConsoleBackend(TestNotificationBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestNotificationDjangoEmailBackend(TestNotificationBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestNotificationLoggerBackend(TestNotificationBackend):

    def tests_written(self):
        assert_equals(True, "Test written")


class TestNotificationTestBackend(TestNotificationBackend):

    def tests_written(self):
        assert_equals(True, "Test written")
