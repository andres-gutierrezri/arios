import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler'

        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
