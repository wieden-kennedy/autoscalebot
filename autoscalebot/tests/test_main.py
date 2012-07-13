from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from autoscalebot.tests import *


class TestMain:

    def setUp(self):
        self.test_scaler

    def tests_written(self):
        assert_equals(True, "Test written")

    def test_heartbeats_run(self):
        assert_equals(True, "Test written")

    def test_history_clears_after_scale(self):
        assert_equals(True, "Test written")

    def test_history_stays_trimmed(self):
        assert_equals(True, "Test written")

    def test_all_backends_get_setup_called(self):
        assert_equals(True, "Test written")

    def test_all_backends_get_teardown_called(self):
        assert_equals(True, "Test written")

    def test_all_backends_get_start_heartbeat_called(self):
        assert_equals(True, "Test written")
