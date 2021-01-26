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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.environ.get('eva_ruta_log',
                                       os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                    'eva.log')),
            'maxBytes': 10 * 1024 * 1024,
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
