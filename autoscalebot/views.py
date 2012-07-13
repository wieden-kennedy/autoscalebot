import tempfile
from django.core.cache import cache
from django.http import HttpResponse

from autoscalebot.models import HeartbeatTestData


def heartbeat(request):
    # Hit the database
    rand_number = "%s" % HeartbeatTestData.objects.order_by('?')[0].number

    # Grab from the cache
    cached_val = cache.get('autoscalebot-cached-value')
    if not cached_val:
        cache.set('autoscalebot-cached-value', "1234")
        cached_val = cache.get('autoscalebot-cached-value')

    # Read and write the filesystem
    t = tempfile.TemporaryFile()
    t.write("%s %s" % (rand_number, cached_val))
    t.flush()
    t.seek(0)
    assert "%s %s" % (rand_number, cached_val) == t.read()
    t.close()

    # Respond
    return HttpResponse("Beat", content_type="text/plain")
