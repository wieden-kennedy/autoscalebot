Django-heroku-autoscale has one simple aim: to make scaling on heroku something you can stop worrying about.


Installing
==========

Easy:


1. ```pip install heroku-autoscale```

2. settings.py: ```INSTALLED_APPS += ("heroku_autoscale",)```

3. Set the required settings:

    * `AUTOSCALE_HEROKU_APP_NAME`
    * `AUTOSCALE_HEROKU_API_KEY`

3. Tune your app (optional, but reccomended)
4. Add it to your Procfile:

    ```
    autoscaleworker: project/manage.py do_autoscale
    ```


Usage
=====

How it works
------------

Heroku-autoscale pings a heartbeat URL, and makes sure the response time is within the limits you've defined.  If it's outside those bounds (for long enough), it scales up or down your app as needed.  Every part of that description is configurable via the settings.  Note that running heroku-autoscale will require one worker dyno, so if you're hobbying it, running one dyno most of the time, it won't save you cash.


Tuning autoscale
----------------

Heroku-autoscale has a bunch of settings, so you should be able to tune it for most needs.

* `AUTOSCALE_HEROKU_APP_NAME` 
    
    * *Required*.  The name of your app, ie "dancing-forest-1234".

* `AUTOSCALE_HEROKU_API_KEY`
    
    * *Required*. Your API key - you can get it on your [account page](https://api.heroku.com/account).

* `AUTOSCALE_HEARTBEAT_INTERVAL_IN_SECONDS` 

    * the number of seconds between heartbeat checks. Defaults to `30`.

* `AUTOSCALE_HEARTBEAT_URL` 

    * the url autoscale should hit, and expect a response in a given time. Defaults to `/heroku-autoscale/heartbeat/v1`

* `AUTOSCALE_MAX_RESPONSE_TIME_IN_MS` 

    * the maximum time a response can take, before it counts as "too slow". Defaults to `1000`.

* `AUTOSCALE_MIN_RESPONSE_TIME_IN_MS` 

    * the minimum time a response can take, before it counts as "too fast". Defaults to `200`.

* `AUTOSCALE_NUMBER_OF_FAILS_TO_SCALE_UP_AFTER` 

    * the number of consecutive fails before autoscale adds dynos. Defaults to `3`.

* `AUTOSCALE_NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER` 

    * the number of consecutive passes before autoscale removes dynos. Defaults to `5`.

* `AUTOSCALE_MAX_DYNOS` 

    * the absolute maximum number of dynos. Default to `3`. This value is either an integer, or a dictionary of time/max pairs.  E.g.

        ```python
        # sets the absolute max as 5 dynos
        AUTOSCALE_MAX_DYNOS = 5

        # Sets the max as 5 dynos from 9am-5pm local time, and 2 dynos otherwise.
        AUTOSCALE_MAX_DYNOS = {
            "0:00" = 2,
            "9:00" = 5,
            "17:00" = 2
        }

        # If you're using time-based settings, don't forget to set:
        TIME_ZONE = 'America/Vancouver'
        ```

* `AUTOSCALE_MIN_DYNOS` 

    * the absolute minimum number of dynos. Default to `1`. This value is either an integer, or a dictionary of time/max pairs. E.g.

        ```python
        # sets the absolute min as 2 dynos
        AUTOSCALE_MIN_DYNOS = 2

        # Sets the min as 3 dynos from 8am-6pm local time, and 1 dyno otherwise.
        AUTOSCALE_MIN_DYNOS = {
            "0:00" = 1,
            "8:00" = 3,
            "18:00" = 1
        }
        ```

* `AUTOSCALE_INCREMENT` 
    * the number of dynos to add or remove on scaling. Defaults to `1`.

* `AUTOSCALE_NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD` 
    * Paired with the setting below, this setting will send an email to the ADMIN email if the scale differential in the given time period exceeds the threshold.  For example, if I see a scale of more than 10 dynos within 30 minutes, something intesting is happening with the side.  I'd probably like to know.  Defaults to `None`, and is disabled.

* `AUTOSCALE_NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES` 
    * The time period to count differentials over. Defaults to `None`

* `AUTOSCALE_NOTIFY_IF_NEEDS_EXCEED_MAX`
    * Send an email to the ADMIN when the app is at AUTOSCALE_MAX_DYNOS, and is the reponses are too slow. This likely means that AUTOSCALE_MAX_DYNOS is too low, but django-heroku-autoscale won't scale it up without your explicit instructions. Defaults to `True`

* `AUTOSCALE_NOTIFY_IF_NEEDS_BELOW_MIN`
    * Send an email to the ADMIN when the app is at AUTOSCALE_MIN_DYNOS, and is the reponses are below the scale down minimum (but above one).  Useful for learning if you have AUTOSCALE_MIN_DYNOS set too low. Defaults to `False`

* `AUTOSCALE_NOTIFY_ON_SCALE_FAILS`
    * Send an email to the ADMIN if a call to the scaling API fails for any reason. Note that a scale fail doesn't hurt anything, and scaling will be attempted again in the next heartbeat. Defaults to `False`


Making a good heartbeat URL
---------------------------

The best heartbeat url will test against the bottlenecks your app is most likely to have as it scales up.  The default url hits the cache, database, and disk IO.  To make autoscale fit your app, you're best off writing a custom view that emulates your user's most common actions.


Collectstatic gotcha, and some delightful side-effects of autoscale
-------------------------------------------------------------------

There's a truth about Heroku and all other cloud-based services:  If no traffic hits your dyno, they quietly shut it down until a request comes in.  Normally, that's not a big deal, but due to a confluence of collectstatic looking on the local filesystem for caching, and heroku's read-only (ish) filesystem on dynos, the sanest way to handle static files on heroku is often with a Procfile like this:

    ```
    web: project/manage.py collectstatic --noinput --settings=envs.live;python project/manage.py run_gunicorn -b "0.0.0.0:$PORT" --workers=4 --settings=envs.live
    ```

The problem, of course, is that once Heroku kills your dyno, the new one has to re-run collectstatic before it can serve the request - and that can take a while.  `django-heroku-autoscale`'s heartbeats have a very nice side effect: if you set them low enough (every few minutes), and you're properly minimally sized, each dyno will get traffic, and Heroku will never kill them off.


Using autoscale outside django
------------------------------

heroku-autoscale should generally work outside django, but it hasn't been heavily tested.  Here's what you'd need to do:

1. Get your settings injected into the settings file.  (or, provide them as a dictionary-like object at django.conf.settings)
2. Fire up a single, long-running thread that will be restarted.
3. In that thread, run:

    ```python
    from heroku_autoscale.tasks import start_heartbeat
    start_heartbeat()
    ```



Recent updates (full log in CHANGES)
------------------------------------

*0.1*

* Initial release


Credits:
========

This package is not written, maintained, or in any way affiliated with Heroku.  "Heroku" is copyright Heroku.

Code credits for heroku-autoscale itself are in the AUTHORS file.