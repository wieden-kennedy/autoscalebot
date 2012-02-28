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

    * `AUTOSCALE_HEROKU_APP_NAME`
    * `AUTOSCALE_HEROKU_API_KEY`

3. If you want the built-in test view (v0.2):
    
    * settings.py: 

        ```INSTALLED_APPS += ("heroku_web_autoscale",)```

    * urls.py: 
        ```urlpatterns += patterns('',
               url(r'^', include('heroku_web_autoscale.urls', app_name="heroku_web_autoscale", namespace="heroku_web_autoscale"), ),
            )```

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

* `HEARTBEAT_INTERVAL_IN_SECONDS` 

    * the number of seconds between heartbeat checks. Defaults to `30`.

* `HEARTBEAT_URL` 

    * the url autoscale should hit, and expect a response in a given time. Defaults to `/heroku-autoscale/heartbeat/v1`

* `MAX_RESPONSE_TIME_IN_MS` 

    * the maximum time a response can take, before it counts as "too slow". Defaults to `1000`.

* `MIN_RESPONSE_TIME_IN_MS` 

    * the minimum time a response can take, before it counts as "too fast". Defaults to `200`.

* `NUMBER_OF_FAILS_TO_SCALE_UP_AFTER` 

    * the number of consecutive fails (timeouts or 500s) before autoscale adds dynos. Defaults to `3`.

* `NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER` 

    * the number of consecutive passes before autoscale removes dynos. Defaults to `5`.

* `MAX_DYNOS` 

    * the absolute maximum number of dynos. Default to `3`. This value is either an integer, or (v0.2) a dictionary of time/max pairs.  E.g.

        ```python
        # sets the absolute max as 5 dynos
        MAX_DYNOS = 5

        # Sets the max as 5 dynos from 9am-5pm local time, and 2 dynos otherwise.
        MAX_DYNOS = {
            "0:00" = 2,
            "9:00" = 5,
            "17:00" = 2
        }

        # If you're using time-based settings, don't forget to set:
        TIME_ZONE = 'America/Vancouver'
        ```

* `MIN_DYNOS` 

    * the absolute minimum number of dynos. Default to `1`. This value is either an integer, or (v0.2) a dictionary of time/max pairs. E.g.

        ```python
        # sets the absolute min as 2 dynos
        MIN_DYNOS = 2

        # Sets the min as 3 dynos from 8am-6pm local time, and 1 dyno otherwise.
        MIN_DYNOS = {
            "0:00" = 1,
            "8:00" = 3,
            "18:00" = 1
        }
        ```

* `INCREMENT` 
    * the number of dynos to add or remove on scaling. Defaults to `1`.

* `NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD` 
    * (v0.2) Paired with the setting below, this setting will send an email to the `ADMINS` email if the scale differential in the given time period exceeds the threshold.  For example, if I see a scale of more than 10 dynos within 30 minutes, something intesting is happening with the side.  I'd probably like to know.  Defaults to `None`, and is disabled.

* `NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES` 
    * (v0.2) The time period to count differentials over. Defaults to `None`.

* `NOTIFY_IF_NEEDS_EXCEED_MAX`
    * (v0.2) Send an email to the `ADMINS` when the app is at `MAX_DYNOS`, and the reponses are too slow. This likely means that `MAX_DYNOS` is too low, but django-heroku-autoscale won't scale it up without your explicit instructions. Defaults to `True`.

* `NOTIFY_IF_NEEDS_BELOW_MIN`
    * (v0.2) Send an email to the `ADMINS` when the app is at `MIN_DYNOS`, and the reponses are below the scale down minimum (but above one).  Useful for learning if you have `MIN_DYNOS` set too low. Defaults to `False`.

* `NOTIFY_ON_SCALE_FAILS`
    * (v0.2) Send an email to the `ADMINS` if a call to the scaling API fails for any reason. Note that a scale fail doesn't hurt anything, and scaling will be attempted again in the next heartbeat. Defaults to `False`.


Making a good heartbeat URL
---------------------------

The best heartbeat url will test against the bottlenecks your app is most likely to have as it scales up.  The bundled django app provides a url that hits the cache, database, and disk IO.  To make autoscale fit your app, you're best off writing a custom view that emulates your user's most common actions.


Django's staticfiles gotcha, and some delightful side-effects of autoscale
----------------------------------------------------------------------------

There's a truth about Heroku and all other cloud-based services:  If no traffic hits your dyno, they quietly shut it down until a request comes in.  Normally, that's not a big deal, but due to a confluence of staticfiles looking at the local filesystem for unique-filename caching, and heroku's read-only (ish) filesystem on dynos, the sanest way to handle static files on heroku is often with a Procfile like this:

    ```
    web: project/manage.py collectstatic --noinput;python project/manage.py run_gunicorn -b "0.0.0.0:$PORT" --workers=4
    ```

The problem, of course, is that once Heroku kills your dyno, the new one has to re-run collectstatic before it can serve the request - and that can take a while.  `django-heroku-autoscale`'s heartbeats have a very nice side effect: if you set them low enough (every couple minutes for small sites), and you're properly minimally sized, each dyno will get traffic, and Heroku will never kill them off.

Roadmap 
------------------------------------

*0.2*

* Better django integration (test url and view)
* Time-based MAX and MIN settings
* Notifications



Recent updates (full log in CHANGES)
------------------------------------

*0.1*

* Initial release


Credits:
========

This package is not written, maintained, or in any way affiliated with Heroku.  "Heroku" is copyright Heroku.

Code credits for heroku-web-autoscale itself are in the AUTHORS file.