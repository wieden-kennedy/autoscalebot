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


Usage
=====

Getting it set up
-----------------


How it works
------------

Heroku-autoscale pings a heartbeat URL, and makes sure the response time is within the limits you've defined.  If it's outside those bounds (for long enough), it scales up or down your app as needed.  Every part of that description is configurable via the settings.


Tuning autoscale
----------------

`heroku-autoscale` has a bunch of settings, so you should be able to tune it for most needs.

AUTOSCALE_HEROKU_APP_NAME - *Required*.  The name of your app, ie "dancing-forest-1234".

AUTOSCALE_HEROKU_API_KEY - *Required*. Your API key - you can get it on your [account page](https://api.heroku.com/account).

AUTOSCALE_HEARTBEAT_INTERVAL_IN_SECONDS - the number of seconds between heartbeat checks. Defaults to 30.

AUTOSCALE_HEARTBEAT_URL - the url autoscale should hit, and expect a response in a given time. Defaults to `/heroku-autoscale/heartbeat/v1`

AUTOSCALE_MAX_RESPONSE_TIME_IN_MS - the maximum time a response can take, before it counts as "failing". Defaults to `1000`

AUTOSCALE_MIN_RESPONSE_TIME_IN_MS - the minimum time a response can take, before it counts as "passing". Defaults to `200`

AUTOSCALE_NUMBER_OF_FAILS_TO_SCALE_UP_AFTER - the number of consecutive fails before autoscale adds dynos. Defaults to `3`

AUTOSCALE_NUMBER_OF_PASSES_TO_SCALE_DOWN_AFTER - the number of consecutive passes before autoscale removes dynos. Defaults to `5`

AUTOSCALE_MAX_DYNOS - the absolute maximum number of dynos. Default is 3. This value is either an integer, or a dictionary of time/max pairs.  E.g.

    ```python
    # sets the absolute max as 5 dynos
    AUTOSCALE_MAX_DYNOS = 5

    # Sets the max as 5 dynos from 9 am-5pm local time, and 2 dynos otherwise.
    AUTOSCALE_MAX_DYNOS = {
        "0:00" = 2,
        "9:00" = 5,
        "17:00" = 2
    }
    ```

AUTOSCALE_MIN_DYNOS - the absolute minimum number of dynos. Default is 1. This value is either an integer, or a dictionary of time/max pairs. E.g.

    ```python
    # sets the absolute min as 2 dynos
    AUTOSCALE_MIN_DYNOS = 2

    # Sets the min as 3 dynos from 9 am-5pm local time, and 1 dyno otherwise.
    AUTOSCALE_MIN_DYNOS = {
        "0:00" = 1,
        "9:00" = 3,
        "17:00" = 1
    }
    ```

AUTOSCALE_INCREMENT - the number of dynos to add or remove on scaling. Default is 1.

AUTOSCALE_NOTIFY_IF_SCALE_DIFF_EXCEEDS_THRESHOLD - Paired with the setting below, this setting will send an email to the ADMIN email if the scale differential in the given time period exceeds the threshold.  For example, if I see a scale of more than 10 dynos within 30 minutes, something intesting is happening with the side.  I'd probably like to know.  Defaults to None, and is disabled.

AUTOSCALE_NOTIFY_IF_SCALE_DIFF_EXCEEDS_PERIOD_IN_MINUTES - The time period to count differentials over.


Making a good heartbeat URL
---------------------------

The best heartbeat url will test against the bottlenecks your app is most likely to have as it scales up.  The default url hits the cache, database, and disk IO.  To make autoscale fit your app, you're best off writing a custom view that emulates your user's most common actions.


Collectstatic gotchas in django
-------------------------------




Recent updates (full log in CHANGES)
------------------------------------

*0.1*

* Initial release


Credits:
========

This package is not written, maintained, or in any way related to Heroku.  It

Code credits for salad itself are in the AUTHORS file.