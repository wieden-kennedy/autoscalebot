from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from autoscalebot.conf import AutoscaleSettings
from autoscalebot.models import AutoscaleBot
from autoscalebot.tests import *


class TestDecisionBackend:

    def setUp(self):
        self.backend


class TestDecisionBaseBackend(TestDecisionBackend):

    def setUp(self):
        test_settings = AutoscaleSettings(settings={
                'DECISION': {
                    'BACKEND': 'autoscalebot.backends.decision.base.BaseDecisionBackend',
                }
            })
        self.autoscalebot = AutoscaleBot("test", test_settings)
        self.backend = autoscalebot.measurement_backend

    # def test_scale_up_does_not_exceed_max(self):
    #     assert_equals(True, "Test written")

    # def test_scale_up_does_not_exceed_min(self):
    #     assert_equals(True, "Test written")

    # def test_increment(self):
    #     assert_equals(True, "Test written")

    # def test_get_correct_edges_from_timestamp(self):
    #     assert_equals(True, "Test written")

    # def test_defaults(self):
    #     assert_equals(True, "Test written")

    # def tests_written(self):
    #     assert_equals(True, "Test written")

    def test_cmp_time_string(self):
        assert_equals(self.backend._cmp_time_string("1:00", "2:00"), -1)
        assert_equals(self.backend._cmp_time_string("2:00", "1:00"), 1)
        assert_equals(self.backend._cmp_time_string("2:00", "1:50"), 1)
        assert_equals(self.backend._cmp_time_string("2:00", "15:50"), -1)
        assert_equals(self.backend._cmp_time_string("2:00", "15:00"), -1)
        assert_equals(self.backend._cmp_time_string("23:59", "0:00"), 1)
        assert_equals(self.backend._cmp_time_string("12:00", "12:00"), 0)


# class TestDecisionIncrementBackend(TestDecisionBackend):

#     def test_scale_up_does_not_exceed_max(self):
#         assert_equals(True, "Test written")

#     def test_scale_up_does_not_exceed_min(self):
#         assert_equals(True, "Test written")

#     def test_increment(self):
#         assert_equals(True, "Test written")

#     def test_get_correct_edges_from_timestamp(self):
#         assert_equals(True, "Test written")

#     def test_scale_to_the_right_number_in_several_scenarios(self):
#         assert_equals(True, "Test written")

#     def test_defaults(self):
#         assert_equals(True, "Test written")

#     def tests_written(self):
#         assert_equals(True, "Test written")


# class TestDecisionAverageBackend(TestDecisionBackend):

#     def test_scale_up_does_not_exceed_max(self):
#         assert_equals(True, "Test written")

#     def test_scale_up_does_not_exceed_min(self):
#         assert_equals(True, "Test written")

#     def test_increment(self):
#         assert_equals(True, "Test written")

#     def test_get_correct_edges_from_timestamp(self):
#         assert_equals(True, "Test written")

#     def test_scale_to_the_right_number_in_several_scenarios(self):
#         assert_equals(True, "Test written")

#     def test_defaults(self):
#         assert_equals(True, "Test written")

#     def tests_written(self):
#         assert_equals(True, "Test written")


# class TestDecisionConsecutiveBackend(TestDecisionBackend):

#     def test_scale_up_does_not_exceed_max(self):
#         assert_equals(True, "Test written")

#     def test_scale_up_does_not_exceed_min(self):
#         assert_equals(True, "Test written")

#     def test_increment(self):
#         assert_equals(True, "Test written")

#     def test_get_correct_edges_from_timestamp(self):
#         assert_equals(True, "Test written")

#     def test_scale_to_the_right_number_in_several_scenarios(self):
#         assert_equals(True, "Test written")

#     def test_defaults(self):
#         assert_equals(True, "Test written")

#     def tests_written(self):
#         assert_equals(True, "Test written")
