from django.conf.urls.defaults import patterns, url
from heroku_web_autoscale import views

urlpatterns = patterns('',
    url(r'heartbeat', views.heartbeat, name='heartbeat'),
)
