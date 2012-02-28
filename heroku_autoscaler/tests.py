import time
import urllib2
from nose.tools import assert_equals
from heroku_autoscaler import TOO_LOW, JUST_RIGHT, TOO_HIGH
from heroku_autoscaler.conf import settings
from heroku_autoscaler.models import HerokuAutoscaler

settings.HEROKU_APP_NAME = "test-app"
settings.HEROKU_API_KEY = "1234567"
settings.HEARTBEAT_INTERVAL_IN_SECONDS = 30
settings.HEARTBEAT_URL = 'http://www.google.com'
settings.MAX_RESPONSE_TIME_IN_MS = 1000
settings.MIN_RESPONSE_TIME_IN_MS = 400
settings.NUMBER_OF_FAILS_TO_SCALE_UP_AFTER = 3
settings.NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER = 5
settings.MAX_DYNOS = 3
settings.MIN_DYNOS = 1
settings.INCREMENT = 1
settings.NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD = None
settings.NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES = None
settings.NOTIFY_IF_NEEDS_EXCEED_MAX = True
settings.NOTIFY_IF_NEEDS_BELOW_MIN = False


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


class MockHerokuApp:

    @property
    def processes(self):
        if not hasattr(self, "_processes"):
            self._processes = {'web': MockHerokuProcesses(), }
        return self._processes


class MockHerokuAutoscaler(HerokuAutoscaler):
    @property
    def heroku_app(self):
        if not hasattr(self, "_heroku_app"):
            self._heroku_app = MockHerokuApp()
        return self._heroku_app


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
            self._test_scaler = MockHerokuAutoscaler()
        return self._test_scaler

    def test_heroku_scale(self):
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.heroku_scale(5)
        assert_equals(self.test_scaler.num_dynos, 5)
        self.test_scaler.heroku_scale(2)
        assert_equals(self.test_scaler.num_dynos, 2)

    def test_num_dynos(self):
        self.test_scaler.heroku_scale(5)
        assert_equals(len([i for i in self.test_scaler.heroku_app.processes['web']]), 5)

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
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 3)
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
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 2)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 1)
        self.test_scaler.do_autoscale()
        assert_equals(self.test_scaler.num_dynos, 1)

    def test_time_based_scale_up_works(self):
        assert True == "Test written"

    def test_time_based_scale_down_works(self):
        assert True == "Test written"

    def test_custom_increments_work(self):
        assert True == "Test written"

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
        assert True == "Test written"

    def test_notify_if_scale_diff_exceeds_period_in_minutes_works(self):
        assert True == "Test written"

    def test_notify_if_needs_exceed_max_works(self):
        assert True == "Test written"

    def test_notify_if_needs_below_min_works(self):
        assert True == "Test written"

    def test_notify_on_scale_fails_works(self):
        assert True == "Test written"

# TODO:
    # django tests
