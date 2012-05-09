class BaseBackend(object):
    """
    This class is the base backend, and serves largely as a scaffolding
    for other backends.  It implements a common core of methods for setup,
    teardown, and heartbeat_start.
    """

    def __init__(self, autoscalebot, *args, **kwargs):
        self.autoscalebot = autoscalebot
        super(BaseBackend, self).__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        super(BaseBackend, self).setup(*args, **kwargs)

    def teardown(self, *args, **kwargs):
        super(BaseBackend, self).teardown(*args, **kwargs)

    def heartbeat_start(self, *args, **kwargs):
        super(BaseBackend, self).heartbeat_start(*args, **kwargs)
