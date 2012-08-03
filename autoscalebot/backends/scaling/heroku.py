import heroku
from autoscalebot.backends.scaling.base import BaseScalingBackend


class HerokuBackend(BaseScalingBackend):
    """
    This is the base scaling class
    """
    def __init__(self, *args, **kwargs):
        self.DEFAULT_BACKEND_SETTINGS = {}
        super(HerokuBackend, self).__init__(*args, **kwargs)

    def heartbeat_start(self, *args, **kwargs):
        super(HerokuBackend, self).heartbeat_start(*args, **kwargs)
        self._num_processes = None

    @property
    def heroku_app(self):
        if not hasattr(self, "_heroku_app"):
            cloud = heroku.from_key(self.settings.API_KEY)
            self._heroku_app = cloud.apps[self.settings.APP_NAME]
        return self._heroku_app

    def scale_to(self, num_requested):
        try:
            self.heroku_app.processes[self.settings.process_name].scale(num_requested)
            self.notification("notify_scaled")

        except:
            self.notification("notify_scale_failed")

    def get_num_processes(self):
        if not hasattr(self, "_num_processes") or not self._num_processes:
            self._num_processes = len([1 for i in self.heroku_app.processes[self.process_name]])
        return self._num_processes
