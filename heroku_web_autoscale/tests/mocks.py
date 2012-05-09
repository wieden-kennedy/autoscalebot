import time
from heroku_web_autoscale.conf import AutoscaleSettings
from heroku_web_autoscale.models import AutoscaleBot


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
test_settings.NOTIFICATION_BACKENDS = ["heroku_web_autoscale.backends.notification.TestBackend", ]


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


class MockAutoscaleBot(AutoscaleBot):

    def __init__(self, *args, **kwargs):
        super(MockAutoscaleBot, self).__init__(*args, **kwargs)
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

