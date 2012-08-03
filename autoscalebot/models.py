import time


def _get_instantiated_class(backend_settings, autoscalebot):
    # Split up the backend and its module
    print "backend_settings", backend_settings
    backend_name = backend_settings.BACKEND
    module_name = backend_name[:backend_name.rfind(".")]
    class_name = backend_name[backend_name.rfind(".") + 1:]
    # Import the module
    m = __import__(module_name, globals(), locals(), [class_name, ])
    # Instantiate the class, passing this autoscalebot, and return it
    return getattr(m, class_name)(autoscalebot)


class AutoscaleBot(object):
    def __init__(self, nickname, process_settings, *args, **kwargs):
        super(AutoscaleBot, self).__init__(*args, **kwargs)
        self.nickname = nickname
        self.settings = process_settings
        self.results = []
        self.measurement_backend = None
        self.decision_backend = None
        self.scaling_backend = None
        self.alive = True
        self.notification_backends = []

        # Setup backends
        self.measurement_backend = _get_instantiated_class(self.settings.MEASUREMENT, self)
        self.decision_backend = _get_instantiated_class(self.settings.DECISION, self)
        self.scaling_backend = _get_instantiated_class(self.settings.SCALING, self)

        # # Setup notification backends.
        # if self.settings.NOTIFICATION.BACKENDS:
        #     for b in self.settings.NOTIFICATION.BACKENDS:
        #         self.notification_backends.append(_get_instantiated_class(b, self))

        backend_and_setting_pairs = [
            (self.measurement_backend, self.settings.MEASUREMENT.SETTINGS),
            (self.decision_backend, self.settings.DECISION.SETTINGS),
            (self.scaling_backend, self.settings.SCALING.SETTINGS),
        ]

        # Add backend defaults to settings
        for backend, backend_settings in backend_and_setting_pairs:
            print backend_settings
            for setting_key in ["DEFAULT_BASE_SETTINGS", "DEFAULT_BACKEND_SETTINGS"]:
                if hasattr(backend, setting_key):
                    for k, v in getattr(backend, setting_key).iteritems():
                        if not hasattr(backend_settings, k):
                            setattr(backend_settings, k, v)
        print self.settings.__dict__

    def notification(self, fn, *args, **kwargs):
        for b in self.notification_backends:
            f = getattr(b, fn)
            f(*args, **kwargs)

    def get_measurement(self, *args, **kwargs):
        result = self.measurement_backend.measure()

        if self.settings.NOTIFY_ON_EVERY_MEASUREMENT:
            self.notification("ping_complete", result)

        return result

    def get_num_of_processes_to_scale_to(self):
        return self.decision_backend.get_num_to_scale_to(self.results)

    def add_to_history(self, result):
        self.results.append(result)

        if len(self.results) > self.settings.DECISION.HISTORY_LENGTH:
            self.results = self.results[-1 * self.settings.DECISION.HISTORY_LENGTH:]

    def heartbeat_and_wait(self, *args, **kwargs):
        # Tell the backends we're starting another heartbeat (clear cached vars, etc)
        self.measurement_backend.heartbeat_start()
        self.decision_backend.heartbeat_start()
        self.scaling_backend.heartbeat_start()
        [b.heartbeat_start() for b in self.notification_backends]

        r = self.get_measurement()
        self.add_to_history(r)

        num = self.get_num_of_processes_to_scale_to()
        did_scale = self.scaling_backend.scale_to(num)
        sleep_time = self.settings.MEASUREMENT.INTERVAL_IN_SECONDS
        if did_scale:
            sleep_time += self.settings.DECISION.POST_SCALE_WAIT_TIME_SECONDS
            # clear results
            self.results = []
        time.sleep(sleep_time)

    def setup(self, *args, **kwargs):
        self.measurement_backend.setup()
        self.decision_backend.setup()
        self.scaling_backend.setup()
        [b.setup() for b in self.notification_backends]

        while self.alive:
            self.heartbeat_and_wait()

    def teardown(self, *args, **kwargs):
        self.alive = False
        self.measurement_backend.teardown()
        self.decision_backend.teardown()
        self.scaling_backend.teardown()
        [b.teardown() for b in self.notification_backends]


try:
    from django.db import models

    class HeartbeatTestData(models.Model):
        number = models.IntegerField(blank=False, null=False)

except:
    pass
