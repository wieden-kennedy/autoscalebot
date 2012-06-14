from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from heroku_web_autoscale.tests import *


class TestDecisionBackend:

    def setUp(self):
        self.test_scaler


class TestDecsionBaseBackend(TestDecisionBackend):

    def test_scale_up_does_not_exceed_max(self):
        assert_equals(True, "Test written")

    def test_scale_up_does_not_exceed_min(self):
        assert_equals(True, "Test written")

    def test_increment(self):
        assert_equals(True, "Test written")

    def test_get_correct_edges_from_timestamp(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")


class TestDecsionIncrementBackend(TestDecisionBackend):

    def test_scale_up_does_not_exceed_max(self):
        assert_equals(True, "Test written")

    def test_scale_up_does_not_exceed_min(self):
        assert_equals(True, "Test written")

    def test_increment(self):
        assert_equals(True, "Test written")

    def test_get_correct_edges_from_timestamp(self):
        assert_equals(True, "Test written")

    def test_scale_to_the_right_number_in_several_scenarios(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")


class TestDecsionAverageBackend(TestDecisionBackend):

    def test_scale_up_does_not_exceed_max(self):
        assert_equals(True, "Test written")

    def test_scale_up_does_not_exceed_min(self):
        assert_equals(True, "Test written")

    def test_increment(self):
        assert_equals(True, "Test written")

    def test_get_correct_edges_from_timestamp(self):
        assert_equals(True, "Test written")

    def test_scale_to_the_right_number_in_several_scenarios(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")


class TestDecsionConsecutiveBackend(TestDecisionBackend):

    def test_scale_up_does_not_exceed_max(self):
        assert_equals(True, "Test written")

    def test_scale_up_does_not_exceed_min(self):
        assert_equals(True, "Test written")

    def test_increment(self):
        assert_equals(True, "Test written")

    def test_get_correct_edges_from_timestamp(self):
        assert_equals(True, "Test written")

    def test_scale_to_the_right_number_in_several_scenarios(self):
        assert_equals(True, "Test written")

    def test_defaults(self):
        assert_equals(True, "Test written")

    def tests_written(self):
        assert_equals(True, "Test written")
