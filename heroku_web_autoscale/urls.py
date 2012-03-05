from django.conf.urls.defaults import *
from heroku_web_autoscale import views

url = parser.url

urlpatterns = parser.patterns('',
    url(r'heartbeat', views.heartbeat, name='heartbeat'),
)
