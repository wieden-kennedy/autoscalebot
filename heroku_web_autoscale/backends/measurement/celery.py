from heroku_web_autoscale.backends.measurement.base import BaseMeasurementBackend
from heroku_web_autoscale.logger import logger
import redis


class CeleryRedisQueueSizeBackend(BaseMeasurementBackend):
    """
    This backend measures the number of items currently in the celery queue,
    using redis as a backend.  This is only a count of unassigned tasks, not yet
    claimed by any workers.

    It accepts the following parameters:

    queue_name, which defaults to "celery",
    host, which defaults to "localhost",
    port, which defaults to "6379",
    database_number, which defaults to "0"

    It returns a dictionary, with the following format:

    {
        'backend': 'CeleryRedisQueueSizeBackend',
        'data': 20, // tasks
        'success': True,  // assuming it was
    }
    """
    def __init__(self, *args, **kwargs):
        super(CeleryRedisQueueSizeBackend, self).__init__(*args, **kwargs)
        self.queue_name = kwargs.get("queue_name", "celery")
        self.host = kwargs.get("host", "localhost")
        self.port = kwargs.get("port", "localhost")
        self.database_number = kwargs.get("database_number", 0)
        self.max_response_time_in_seconds = kwargs.get("max_response_time_in_seconds", 30)

    def measure(self, *args, **kwargs):
        success = True
        size = 0

        try:
            r = redis.StrictRedis(host=self.host, port=self.port, db=self.database_number)
            size = r.llen(self.queue_name)
            r.disconnect()
        except:
            success = False

        if success:
            logger.debug("Queue size: %s." % size)
        else:
            logger.debug("Error getting response from %s." % self.url)

        return {
            'backend': 'CeleryRedisQueueSizeBackend',
            'data': size,
            'success': success
        }
