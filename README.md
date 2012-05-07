heroku-web-autoscale has one simple aim: to make scaling heroku web dynos something you can stop worrying about.  It also integrates nicely with django.


Installing
==========

If you're using not django:
---------------------------

1. ```pip install heroku-web-autoscale```, and add it to your `requirements.txt`

2. Create a settings file somewhere in your `PYTHON_PATH`. We typically call it `autoscale_settings.py`, but you can call it whatever you like.
3. Set these settings for your app, as well as any optional tuning settings. See autoscale_settings.py.dist for an example.

    ```python
    HEROKU_APP_NAME = "my-app-name"
    HEROKU_API_KEY = "1234567890abcdef1234567890abcdef"
    ```

4. Add autoscale to your `Procfile`:

    ```
    autoscaleworker: heroku_web_autoscaler --settings=autoscale_settings
    ```


If you are using django:
-----------------------

1. ```pip install heroku-web-autoscale```, and add it to your `requirements.txt`

2. Set these required settings in your `settings.py`, as well as any optional tuning settings.  Prefix all names on the settings list below with `AUTOSCALE_`

    ```python
    AUTOSCALE_HEROKU_APP_NAME = "my-app-name"
    AUTOSCALE_HEROKU_API_KEY = "1234567890abcdef1234567890abcdef"
    ```

3. If you want the built-in test view:

    settings.py: 

    ```python
    INSTALLED_APPS += ("heroku_web_autoscale",)
    ```

    urls.py: 

    ```python
    urlpatterns += patterns('',
        url(r'^', include('heroku_web_autoscale.urls', app_name="heroku_web_autoscale", namespace="heroku_web_autoscale"), ),
    )
    ```

4. Add it to your Procfile:

    ```
    autoscaleworker: project/manage.py heroku_web_autoscaler
    ```


Usage
=====

How it works
------------

Heroku-autoscale requests a heartbeat URL, and makes sure the response time is within the limits you've defined.  If it's outside those bounds enough times in a row, it scales up or down your app as needed.  Every part of that description is configurable via the settings.  Note that running heroku-autoscale will require one worker dyno, so if you're hobbying it and running one dyno most of the time, it won't save you any cash. It doesn't have to be run on heroku though - any internet-enabled computer will do.


Available settings
-------------------

Heroku-autoscale has a bunch of settings, so you should be able to tune it for most needs.

* `HEROKU_APP_NAME` 
    
    * *Required*.  The name of your app, ie "dancing-forest-1234".

* `HEROKU_API_KEY`
    
    * *Required*. Your API key - you can get it on your [account page](https://api.heroku.com/account).


* `AUTOSCALE_BACKENDS`

    This is the heart of autoscale's configuration.  It allows for a choice and configuration of measurement, decision, and notification backends. Below is an example, handling scaling for web and celery dynos.  See below for detailed backend documentation.

    ```python
    AUTOSCALE_BACKENDS = {
        'web': {
            'MEASUREMENT': {
                'BACKEND': 'heroku_web_autoscale.backends.measurement.ResponseTimeBackend',
                'SETTINGS': {
                    'MIN_TIME_MS': 500,
                    'MAX_TIME_MS': 1000,
                    'HEARTBEAT_URL' = "/my-custom-heartbeat/"
                }
            },
            'DECISION': {
                'BACKEND': 'heroku_web_autoscale.backends.decision.ConsecutiveThresholdBackend',
                'SETTINGS': {
                    'POST_SCALE_WAIT_TIME_SECONDS': 60,
                }
            },
            'NOTIFICATION': {
                'BACKENDS': [
                    'heroku_web_autoscale.backends.notification.DjangoEmailBackend',
                    'heroku_web_autoscale.backends.notification.ConsoleBackend',
                ],
                'SETTINGS': {},
            }
        },
        'celery': {
            'MEASUREMENT': {
                'BACKEND': 'heroku_web_autoscale.backends.measurement.CeleryQueueSizeBackend',
            },
            'DECISION': {
                'BACKEND': 'heroku_web_autoscale.backends.decision.AverageThresholdBackend',
            },
            'NOTIFICATION': {
                'BACKENDS': [
                    'heroku_web_autoscale.backends.notification.LoggerBackend',
                ],
            }
        },
    }
    ```


Backends
--------
To allow for tuning to your app's particular needs, autoscale provides backends for load measurement, decision-making, and notification.  You can also write your own backend, by subclassing the base class of any of them.  Pull requests for additional backends are also welcome!

There are five backends:  Measure, Interpret, Decide, Scale, and Notify.  Here's what they do:

* Measure: finds out how loaded your app is.
* Interpret: makes a value judgement on that measurement, converting it to scaling instructions
* Decide: decides whether to scale up, down, or stay steady based on recent information
* Scale: performs the scale
* Notify: informs administrators.



### Measurement backends

These backends are responsible for querying, pinging, or otherwise measuring the responsiveness of an app. They return a dictionary with those results.

The backends, with their possible settings and default values.

* `ResponseTimeBackend`
    
    Scales based on a set of response times for a given url.

    * `HEARTBEAT_URL` = "/heroku-autoscale/heartbeat/"
    * `HEARTBEAT_INTERVAL_IN_SECONDS` = 30

    Returns:

    ```python
    {
        'backend': 'ResponseTimeBackend',
        'time': 350, // ms
    }
    ```

* `ServiceTimeBackend`

    Scales based on the internal service time of the last heartbeat response.

    * `SCALE_DOWN_TIME_MS` = 200
    * `SCALE_UP_TIME_MS` = 1000
    * `HEARTBEAT_URL` = "/heartbeat"
    * `HEARTBEAT_INTERVAL_IN_SECONDS` = 30

* `CeleryQueueSizeBackend`

    Scales based on the number of waiting Celery tasks.

    * `SCALE_DOWN_SIZE` = 0
    * `SCALE_UP_SIZE` = 10

* `AppDecisionBackend`

    Expects `'SCALE_UP'`, `'SCALE_DOWN'` or `'STEADY'` to be returned by the app, and passes them on directly.



### Interpretation backends

These backends are responsible turning the measurement results into `SCALE_UP`, `SCALE_DOWN`, or `STEADY`.  They are passed the current number of dynos, the request timestamp, and the measurement backend results

The backends, with their possible settings and default values.

* `ResponseTimeBackend`
    
    Scales based on a set of response times for a given url.

    * `SCALE_DOWN_TIME_MS` = 400
    * `SCALE_UP_TIME_MS` = 1200
    * `HEARTBEAT_URL` = "/heroku-autoscale/heartbeat/"
    * `HEARTBEAT_INTERVAL_IN_SECONDS` = 30

* `ServiceTimeBackend`

    Scales based on the internal service time of the last heartbeat response.

    * `SCALE_DOWN_TIME_MS` = 200
    * `SCALE_UP_TIME_MS` = 1000
    * `HEARTBEAT_URL` = "/heartbeat"
    * `HEARTBEAT_INTERVAL_IN_SECONDS` = 30

* `CeleryQueueSizeBackend`

    Scales based on the number of waiting Celery tasks.

    * `SCALE_DOWN_SIZE` = 0
    * `SCALE_UP_SIZE` = 10

* `AppDecisionBackend`

    Expects `'SCALE_UP'`, `'SCALE_DOWN'` or `'STEADY'` to be returned by the app, and passes them on directly.



### Decision Backends

Decision backends decide when to scale, based on the most recent set of responses.

##### All Backends

All decision backends have these three settings:

* `MAX_DYNOS` 

    * the absolute maximum number of dynos. Default to `3`. This value is either an integer, or a dictionary of time/max pairs.  E.g.

        ```python
        # sets the absolute max as 5 dynos
        MAX_DYNOS = 5

        # Sets the max as 5 dynos from 9am-5pm local time, and 2 dynos otherwise.
        MAX_DYNOS = {
            "0:00": 2,
            "9:00": 5,
            "17:00": 2
        }

        # If you're using time-based settings, don't forget to set your time zone.  For django, that's:
        TIME_ZONE = 'America/Vancouver'
        ```

* `MIN_DYNOS` 

    * the absolute minimum number of dynos. Default to `1`. This value is either an integer, or a dictionary of time/max pairs. E.g.

        ```python
        # sets the absolute min as 2 dynos
        MIN_DYNOS = 2

        # Sets the min as 3 dynos from 8am-6pm local time, and 1 dyno otherwise.
        MIN_DYNOS = {
            "0:00": 1,
            "8:00": 3,
            "18:00": 1
        }
        ```

* `INCREMENT` 
    * the number of dynos to add or remove on scaling. Defaults to `1`.

* `POST_SCALE_WAIT_TIME_SECONDS`
    * the number of seconds to wait after scaling before starting evaluation again. Defaults to `5`


##### ConsecutiveThresholdBackend

If the number of consecutive `SCALE_UP` or `SCALE_DOWN` responses exceeds the threshold, do the scale. Available settings:

* `NUMBER_OF_FAILS_TO_SCALE_UP_AFTER` = 3
* `NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER` = 5
* `MAX_DYNOS` = 3
* `MIN_DYNOS` = 1
* `INCREMENT` = 1
* `POST_SCALE_WAIT_TIME_SECONDS` = 5


##### AverageThresholdBackend

If the average result over a given set is `SCALE_UP` or `SCALE_DOWN`, do the scale. Available settings:

* `NUMBER_OF_MEASUREMENTS_TO_AVERAGE` = 3
* `MAX_DYNOS` = 3
* `MIN_DYNOS` = 1
* `INCREMENT` = 1
* `POST_SCALE_WAIT_TIME_SECONDS` = 5

##### ImmediateBackend

Scales based on every heartbeat. Equivalent to using `ConsecutiveThresholdBackend` with `NUMBER_OF_MEASUREMENTS_TO_AVERAGE = 1`.  Available settings:

* `MAX_DYNOS` = 3
* `MIN_DYNOS` = 1
* `INCREMENT` = 1
* `POST_SCALE_WAIT_TIME_SECONDS` = 5



### Notification Backends

Notification backends are there to let you know when scale ups, downs, or other interesting events happen.  Autoscale ships with a few, and pull requests for more are welcome.  All backends take the same setttings.


Notification Backends:

* `ConsoleBackend`, which prints messages to the console, 
* `DjangoEmailBackend`, which emails the `ADMINS` when used in a django project,
* `LoggerBackend`, which sends messages to the python logger.
* `TestBackend`, which adds messages to a list, and is used for unit testing.

Notification Backend Settings:

* `NOTIFY_ON_EVERY_MEASUREMENT` = False
    
    Send a notification with the result of every measurement

* `NOTIFY_ON_EVERY_SCALE` = False

    Send a notification on every scale

* `NOTIFY_IF_NEEDS_BELOW_MIN` = False

    Send a notification if scaling down is called for, but we're already at `MIN_DYNOS`.

* `NOTIFY_IF_NEEDS_EXCEED_MAX` = True

    Send a notification if scaling up is called for, but we're already at `MAX_DYNOS`.

* (v0.4) `NOTIFY_IF_SCALING_IS_TOO_RAPID` = False

    Notify if rapid scaling happens.  This setting is paired with the two below.  If the number of scales is larger than `NOTIFY_IF_SCALING_IS_TOO_RAPID_NUM_SCALES` over the past `NOTIFY_IF_SCALING_IS_TOO_RAPID_TIME_PERIOD_MINUTES`, a notification will be sent.

* (v0.4) `NOTIFY_IF_SCALING_IS_TOO_RAPID_NUM_SCALES` = 5

    This is number of scales (in one direction) that are allowed over the given time period before sending a notification.

* (v0.4) `NOTIFY_IF_SCALING_IS_TOO_RAPID_TIME_PERIOD_MINUTES` = 1

    This is the time period to evaluate the number of scales within.




Making a good heartbeat URL
---------------------------

The best heartbeat url will test against the bottlenecks your app is most likely to have as it scales up.  The bundled django app provides a url that hits the cache, database, and disk IO.  To make autoscale fit your app, you're best off writing a custom view that emulates your user's most common actions.


Django's staticfiles gotcha, and some delightful side-effects of autoscale
----------------------------------------------------------------------------

There's a truth about Heroku and all other cloud-based services:  If no traffic hits your dyno, they quietly shut it down until a request comes in.  Normally, that's not a big deal, but due to a confluence of staticfiles looking at the local filesystem for unique-filename caching, and heroku's read-only (ish) filesystem on dynos, the sanest way to handle static files on heroku is often with a Procfile like this:

    web: project/manage.py collectstatic --noinput;python project/manage.py run_gunicorn -b "0.0.0.0:$PORT" --workers=4


The problem, of course, is that once Heroku kills your dyno, the new one has to re-run collectstatic before it can serve the request - and that can take a while.  `django-heroku-autoscale`'s heartbeats have a very nice side effect: if you set them low enough (every couple minutes for small sites), and you're properly minimally sized, each dyno will get traffic, and Heroku will never kill them off.

Roadmap 
------------------------------------

*0.4*

* Time-based notification thresholds


Releases 
------------------------------------

*0.3*

Huge update. This release splits scaling and load measurement into two new backends, and provides a new streamlined way to configure autoscale's settings.  This update is backwards incompatible. Please see the Backends documentation above for the new settings.


*0.2*

* Better django integration includes a heartbeat url and view
* Time-based MAX and MIN settings
* Notifications via NOTIFICATION_BACKENDS


*0.1*

* Initial release


Credits:
========

This package is not written, maintained, or in any way affiliated with Heroku.  "Heroku" is copyright Heroku.

Code credits for heroku-web-autoscale itself are in the AUTHORS file.