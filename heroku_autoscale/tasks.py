from datetime import timedelta
from celery.decorators import periodic_task
from django.conf import settings


@periodic_task(run_every=timedelta(seconds=settings.AUTOSCALE_HEARTBEAT_INTERVAL_IN_SECONDS))
def beat():
    pass


def scale(dynos=None):

    if dynos:
        # curl -H "Accept: application/json"   -u :api_key -X POST https://api.heroku.com/apps/app-nameprototype/ps/scale -d "qty=1" -d type="web"
        pass

    pass
