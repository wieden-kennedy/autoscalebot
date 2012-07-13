from django.conf.urls.defaults import patterns, url
from autoscalebot import views

urlpatterns = patterns('',
    url(r'heartbeat', views.heartbeat, name='heartbeat'),
)
