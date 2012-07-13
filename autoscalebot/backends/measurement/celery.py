from autoscalebot.backends.measurement.base import BaseMeasurementBackend
from autoscalebot.logger import logger


class CeleryRedisQueueSizeBackend(BaseMeasurementBackend):
    """
    This backend measures the number of items currently in the celery queue,
    using redis as a backend.  This is only a count of unassigned tasks, not yet
    claimed by any workers.

    It accepts the following parameters:

    QUEUE_NAME, which defaults to "celery",
    HOST, which defaults to "localhost",
    PORT, which defaults to "6379",
    DATABASE_NUMBER, which defaults to "0", and

    It returns a dictionary, with the following format:

    {
        'backend': 'CeleryRedisQueueSizeBackend',
        'data': 20, // tasks
        'success': True,  // assuming it was
    }
    """

    def __init__(self, *args, **kwargs):
        BACKEND_SETTINGS = {
            "QUEUE_NAME": "celery",
            "HOST": "localhost",
            "PORT": "6379",
            "DATABASE_NUMBER": "0",
        }
        super(CeleryRedisQueueSizeBackend, self).__init__(*args, **kwargs)
        self.settings = BACKEND_SETTINGS.update(self.settings)

    def measure(self, *args, **kwargs):
        import redis
        success = True
        size = 0

        try:
            r = redis.StrictRedis(host=self.settings.HOST,
                                  port=self.settings.PORT,
                                  db=self.settings.DATABASE_NUMBER,
                                )
            size = r.llen(self.settings.QUEUE_NAME)
            r.disconnect()
        except:
            success = False

        if success:
            logger.debug("Queue size: %s." % size)
        else:
            logger.debug("Error getting response from celery: %s:%s/%s." % (self.settings.HOST, self.settings.PORT, self.settings.DATABASE_NUMBER,))

        return {
            'backend': 'CeleryRedisQueueSizeBackend',
            'data': size,
            'success': success
        }
