from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from heroku_web_autoscale.tests import *


class TestMain:

    def setUp(self):
        self.test_scaler

    def tests_written(self):
        assert_equals(True, "Test written")


class TestDjango(object):

    def tests_written(self):
        assert_equals(True, "Test written")
