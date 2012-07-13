from copy import copy
import datetime
import time
import urllib2
from nose.tools import assert_equals
from nose.plugins.skip import SkipTest
from autoscalebot import TOO_LOW, JUST_RIGHT, TOO_HIGH
from autoscalebot.conf import AutoscaleSettings
from autoscalebot.models import HerokuAutoscaler


class TestSettings(AutoscaleSettings):
    pass

test_settings = TestSettings()

test_settings.HEROKU_APP_NAME = "test-app"
test_settings.HEROKU_API_KEY = "1234567"
test_settings.HEARTBEAT_INTERVAL_IN_SECONDS = 30
test_settings.HEARTBEAT_URL = 'http://www.google.com'
test_settings.MAX_RESPONSE_TIME_IN_MS = 1000
test_settings.MIN_RESPONSE_TIME_IN_MS = 400
test_settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER = 3
test_settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER = 5
test_settings.MAX_DYNOS = 3
test_settings.MIN_DYNOS = 1
test_settings.INCREMENT = 1
test_settings.NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD = None
test_settings.NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES = None
test_settings.NOTIFY_IF_NEEDS_EXCEED_MAX = True
test_settings.NOTIFY_IF_NEEDS_BELOW_MIN = True
test_settings.NOTIFICATION_BACKENDS = ["autoscalebot.backends.notification.TestBackend", ]


class MockHerokuProcesses:
    def __init__(self):
        self.current = 0
        self._processes = [1, ]

    @property
    def processes(self):
        if not hasattr(self, "_processes"):
            self._processes = [1, ]
        return self._processes

    def scale(self, new_num):
        self._processes = [n + 1 for n in range(0, new_num)]

    def __iter__(self):
        return self

    def next(self):
        self.current += 1
        if self.current > len(self.processes):
            raise StopIteration
        else:
            return self.processes[self.current - 1]


class MockBrokenHerokuProcesses(MockHerokuProcesses):

    def scale(self):
        raise Exception


class MockHerokuApp:

    def __init__(self, *args, **kwargs):
        self.processes

    @property
    def processes(self):
        if not hasattr(self, "_processes"):
            self._processes = {'web': MockHerokuProcesses(), }
        return self._processes


class MockBrokenHerokuApp(MockHerokuApp):

    @property
    def processes(self):
        if not hasattr(self, "_processes"):
            self._processes = {'web': MockBrokenHerokuProcesses(), }
        return self._processes


class MockHerokuAutoscaler(HerokuAutoscaler):

    def __init__(self, *args, **kwargs):
        super(MockHerokuAutoscaler, self).__init__(*args, **kwargs)
        self.heroku_app

    @property
    def heroku_app(self):
        if not hasattr(self, "_heroku_app"):
            self._heroku_app = MockHerokuApp()
        return self._heroku_app

    def out_of_band_heroku_scale(self, num_dynos):
        # Ugly mock out of band scale
        self.heroku_app.processes["web"]._processes = [1, 2, 3, 4]
        self._num_dynos = len([i for i in self.heroku_app.processes["web"]._processes])


class MockValidResponse:
    def read(self, *args, **kwargs):
        return "A"


class Mock500Response:
    def read(self, *args, **kwargs):
        raise Exception


def mock_valid_urlopen(self, *args, **kwargs):
    time.sleep(0.5)
    return MockValidResponse()


def mock_invalid_urlopen(self, *args, **kwargs):
    return Mock500Response()


def mock_fast_urlopen(self, *args, **kwargs):
    return MockValidResponse()


def mock_slow_urlopen(self, *args, **kwargs):
    time.sleep(2)
    return MockValidResponse()


class TestHerokuAutoscaler:

    def setUp(self):
        self.test_scaler

    @property
    def test_scaler(self):
        if not hasattr(self, "_test_scaler"):
            self._test_scaler = MockHerokuAutoscaler(test_settings)
        return self._test_scaler

    def test_heroku_scale(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.heroku_scale(3)
        assert_equals(self.test_scaler.num_dynos, 3)
        self.test_scaler.heroku_scale(5)
        assert_equals(self.test_scaler.num_dynos, 3)
        self.test_scaler.heroku_scale(2)
        assert_equals(self.test_scaler.num_dynos, 2)

    def test_num_dynos(self):
        self.test_scaler.heroku_scale(3)
        assert_equals(len([i for i in self.test_scaler.heroku_app.processes['web']]), 3)

    def test_add_to_history(self):
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(JUST_RIGHT)
        assert_equals(self.test_scaler.results, [TOO_LOW, TOO_HIGH, JUST_RIGHT])

    def test_add_to_history_caps_length(self):
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        assert_equals(self.test_scaler.results, [TOO_LOW, TOO_LOW, TOO_LOW, TOO_LOW, TOO_LOW])

    def test_needs_scale_up_works(self):
        self.test_scaler.add_to_history(TOO_LOW)
        assert_equals(self.test_scaler.needs_scale_up, False)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        assert_equals(self.test_scaler.needs_scale_up, True)

    def test_needs_scale_down_works(self):
        self.test_scaler.add_to_history(TOO_HIGH)
        assert_equals(self.test_scaler.needs_scale_down, False)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        assert_equals(self.test_scaler.needs_scale_down, True)

    def test_scale_up(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.scale_up()
        assert_equals(self.test_scaler.num_dynos, 2)

    def test_scale_up_stops_at_limit(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        assert_equals(self.test_scaler.num_dynos, 3)

    def test_scale_down(self):
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        assert_equals(self.test_scaler.num_dynos, 3)
        self.test_scaler.scale_down()
        assert_equals(self.test_scaler.num_dynos, 2)

    def test_scale_down_stops_at_limit(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_down()
        self.test_scaler.scale_down()
        self.test_scaler.scale_down()
        self.test_scaler.scale_down()
        self.test_scaler.scale_down()
        self.test_scaler.scale_down()
        assert_equals(self.test_scaler.num_dynos, 1)

    def test_do_autoscale_up_works(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 2)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 3)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 3)

    def test_do_autoscale_down_works(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        assert_equals(self.test_scaler.num_dynos, 3)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        assert_equals(self.test_scaler.num_dynos, 3)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 2)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 1)

    def test_max_dynos_from_time_based_settings_works(self):
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.MAX_DYNOS = {
            "0:00": 2,
            "9:00": 5,
            "17:00": 3
        }
        now_time = datetime.datetime.now()
        self._test_scaler = MockHerokuAutoscaler(one_off_test_settings)
        early_morning = datetime.datetime(now_time.year, now_time.month, now_time.day, 1, 0)
        mid_day = datetime.datetime(now_time.year, now_time.month, now_time.day, 12, 0)
        evening = datetime.datetime(now_time.year, now_time.month, now_time.day, 18, 0)
        morning_off_by_minutes = datetime.datetime(now_time.year, now_time.month, now_time.day, 9, 5)
        morning_exact = datetime.datetime(now_time.year, now_time.month, now_time.day, 9, 0)
        assert_equals(self.test_scaler.max_num_dynos(when=early_morning), 2)
        assert_equals(self.test_scaler.max_num_dynos(when=mid_day), 5)
        assert_equals(self.test_scaler.max_num_dynos(when=evening), 3)
        assert_equals(self.test_scaler.max_num_dynos(when=morning_off_by_minutes), 5)
        assert_equals(self.test_scaler.max_num_dynos(when=morning_exact), 5)

    def test_min_dynos_from_time_based_settings_works(self):
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.MIN_DYNOS = {
            "0:00": 2,
            "9:00": 5,
            "17:00": 3
        }
        now_time = datetime.datetime.now()
        self._test_scaler = MockHerokuAutoscaler(one_off_test_settings)
        early_morning = datetime.datetime(now_time.year, now_time.month, now_time.day, 1, 0)
        mid_day = datetime.datetime(now_time.year, now_time.month, now_time.day, 12, 0)
        evening = datetime.datetime(now_time.year, now_time.month, now_time.day, 18, 0)
        morning_off_by_minutes = datetime.datetime(now_time.year, now_time.month, now_time.day, 9, 5)
        morning_exact = datetime.datetime(now_time.year, now_time.month, now_time.day, 9, 0)
        assert_equals(self.test_scaler.min_num_dynos(when=early_morning), 2)
        assert_equals(self.test_scaler.min_num_dynos(when=mid_day), 5)
        assert_equals(self.test_scaler.min_num_dynos(when=evening), 3)
        assert_equals(self.test_scaler.min_num_dynos(when=morning_off_by_minutes), 5)
        assert_equals(self.test_scaler.min_num_dynos(when=morning_exact), 5)

    def test_custom_increments_work(self):
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.INCREMENT = 2
        self._test_scaler = MockHerokuAutoscaler(one_off_test_settings)
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 3)

    def test_if_min_is_changed_to_higher_than_current_scaling_works(self):
        self.test_scaler.heroku_scale(1)
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.MIN_DYNOS = 2
        self._test_scaler = MockHerokuAutoscaler(one_off_test_settings)
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 2)

    def test_if_max_is_changed_to_lower_than_current_scaling_works(self):
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.MAX_DYNOS = 2
        self._test_scaler = MockHerokuAutoscaler(one_off_test_settings)
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.out_of_band_heroku_scale(4)

        assert_equals(self.test_scaler.num_dynos, 4)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 2)

    def test_scaling_clears_the_results_queue(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 2)
        assert_equals(self.test_scaler.results, [])

    def test_a_mixed_stack_of_low_high_scales_to_the_min_needed_for_the_condition(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 2)

    def test_ping_and_store_for_valid_url(self):
        urllib2.urlopen = mock_valid_urlopen
        assert_equals(self.test_scaler.results, [])
        self.test_scaler.ping_and_store()
        assert_equals(self.test_scaler.results, [JUST_RIGHT])

    def test_ping_and_store_for_invalid_url(self):
        urllib2.urlopen = mock_invalid_urlopen
        assert_equals(self.test_scaler.results, [])
        self.test_scaler.ping_and_store()
        assert_equals(self.test_scaler.results, [TOO_HIGH])

    def test_ping_and_store_for_slow_url(self):
        urllib2.urlopen = mock_slow_urlopen
        assert_equals(self.test_scaler.results, [])
        self.test_scaler.ping_and_store()
        assert_equals(self.test_scaler.results, [TOO_HIGH])

    def test_ping_and_store_for_fast_url(self):
        urllib2.urlopen = mock_fast_urlopen
        assert_equals(self.test_scaler.results, [])
        self.test_scaler.ping_and_store()
        assert_equals(self.test_scaler.results, [TOO_LOW])

    def test_notify_if_scale_diff_exceeds_threshold_works(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        assert_equals(self.test_scaler.num_dynos, 3)
        print "Feature not written"
        raise SkipTest

    def test_notify_if_scale_diff_exceeds_period_in_minutes_works(self):
        print "Feature not written"
        raise SkipTest

    def test_notify_if_needs_exceed_max_works(self):
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.backends[0].clear_messages()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.do_autoscale()
        assert_equals(len(self.test_scaler.backends[0].messages), 1)
        assert "max" in self.test_scaler.backends[0].messages[0]

    def test_notify_if_needs_below_min_does_not_notify_on_one_dyno_works(self):
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.backends[0].clear_messages()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.do_autoscale()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)

    def test_notify_if_needs_below_min_works(self):
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.MIN_DYNOS = 2
        self._test_scaler = MockHerokuAutoscaler(one_off_test_settings)
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.do_autoscale()
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.backends[0].clear_messages()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.do_autoscale()
        assert_equals(len(self.test_scaler.backends[0].messages), 1)
        assert "min" in self.test_scaler.backends[0].messages[0]

    def test_notify_if_needs_exceed_max_disabled_works(self):
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.NOTIFY_IF_NEEDS_EXCEED_MAX = False
        self._test_scaler = MockHerokuAutoscaler(one_off_test_settings)
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.scale_up()
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.add_to_history(TOO_HIGH)
        self.test_scaler.backends[0].clear_messages()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.do_autoscale()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)

    def test_notify_if_needs_below_min_disabled_works(self):
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.NOTIFY_IF_NEEDS_BELOW_MIN = False
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.add_to_history(TOO_LOW)
        self.test_scaler.backends[0].clear_messages()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.do_autoscale()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)

    def test_notify_on_scale_fails_works(self):
        self.test_scaler._heroku_app = MockBrokenHerokuApp()
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.scale_up()
        assert_equals(len(self.test_scaler.backends[0].messages), 1)
        assert "fail" in self.test_scaler.backends[0].messages[0]

    def test_notify_on_every_scale_works(self):
        assert_equals(len(self.test_scaler.backends[0].messages), 0)
        self.test_scaler.scale_up()
        assert_equals(len(self.test_scaler.backends[0].messages), 1)

    def test_all_backends_are_called_on_notification(self):
        one_off_test_settings = copy(test_settings)
        one_off_test_settings.NOTIFICATION_BACKENDS = [
                                                "autoscalebot.backends.notification.TestBackend",
                                                "autoscalebot.backends.notification.TestBackend"
                                              ]
        self._test_scaler = MockHerokuAutoscaler(one_off_test_settings)
        assert_equals([len(b.messages) for b in self.test_scaler.backends], [0, 0])
        self.test_scaler.scale_up()
        assert_equals([len(b.messages) for b in self.test_scaler.backends], [1, 1])


# TODO: django tests
