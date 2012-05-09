import heroku
from heroku_web_autoscale.backends.scaling.base import BaseScalingBackend


class HerokuScalingBackend(BaseScalingBackend):
    """
    This is the base scaling class
    """
    def __init__(self, *args, **kwargs):
        super(HerokuScalingBackend, self).__init__(*args, **kwargs)
        self.settings = self.autoscalebot.settings.SCALING
        self.process_name = self.autoscalebot.process_name

    @property
    def heroku_app(self):
        if not hasattr(self, "_heroku_app"):
            cloud = heroku.from_key(self.settings.API_KEY)
            self._heroku_app = cloud.apps[self.settings.APP_NAME]
        return self._heroku_app

    def scale_to(self, num_requested):
        try:
            self.heroku_app.processes[self.process_name].scale(num_requested)
            self.notification("notify_scaled")

        except:
            self.notification("notify_scale_failed")

    def get_num_instances(self):
        return len([1 for i in self.heroku_app.processes[self.process_name]])
