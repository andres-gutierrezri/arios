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
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.environ.get('eva_ruta_log',
                                       os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                    'eva.log')),
            'when': 'midnight',
            'backupCount': 0,
            'formatter': 'standard',
            'encoding': 'UTF-8'
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
