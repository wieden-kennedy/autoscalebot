{
    'web': {
        'MEASUREMENT': {
            'BACKEND': 'autoscalebot.backends.measurement.ResponseTimeBackend',
            'SETTINGS': {
                'MIN_TIME_MS': 500,
                'MAX_TIME_MS': 1000,
                'MEASUREMENT_URL': "/my-custom-measurement/",
                'MEASUREMENT_INTERVAL_IN_SECONDS': 30,
                'MIN_PROCESSES': 1,
                'MAX_PROCESSES': 3,
                'INCREMENT': 1,
                'POST_SCALE_WAIT_TIME_SECONDS': 5,
                'HISTORY_LENGTH': 10.
            }
        },
        'DECISION': {
            'BACKEND': 'autoscalebot.backends.decision.ConsecutiveThresholdBackend',
            'SETTINGS': {
                'POST_SCALE_WAIT_TIME_SECONDS': 60,
            }
        },
        'SCALING' : {
            'BACKEND': 'autoscalebot.backends.scaling.HerokuBackend',
            'SETTINGS': {
                'APP_NAME': 'dancing-forest-1234',
                'API_KEY': 'abcdef1234567890abcdef12',
                'WORKER_NAME': 'web'
            }
        },
        'NOTIFICATION': {
            'BACKENDS': [
                'autoscalebot.backends.notification.DjangoEmailBackend',
                'autoscalebot.backends.notification.ConsoleBackend',
            ],
            'SETTINGS': {
                'NOTIFY_ON': ["MEASUREMENT", "SCALE", "BELOW_MIN", "ABOVE_MAX", "TOO_RAPID"],
                'TOO_RAPID_NUM_SCALES': 5,
                'TOO_RAPID_PERIOD_MINUTES': 2
            },
        }

    },
    'celery': {
        'MEASUREMENT': {
            'BACKEND': 'autoscalebot.backends.measurement.CeleryRedisQueueSizeBackend',
        },
        'DECISION': {
            'BACKEND': 'autoscalebot.backends.decision.AverageThresholdBackend',
            'SETTINGS': {
                'MIN_MEASUREMENT_VALUE': 0,
                'MAX_MEASUREMENT_VALUE': 10,
            }
        },
        'SCALING' : {
            'BACKEND': 'autoscalebot.backends.scaling.HerokuBackend',
            'SETTINGS': {
                'APP_NAME': 'dancing-forest-1234',
                'API_KEY': 'abcdef1234567890abcdef12',
            }
        },
        'NOTIFICATION': {
            'BACKENDS': [
                'autoscalebot.backends.notification.LoggerBackend',
            ],
        }
    },
}