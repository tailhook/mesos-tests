import logging.config
from colorlog import ColoredFormatter

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {'()': 'colorlog.ColoredFormatter',
            'format': "%(asctime)s %(log_color)s %(message)s"},
        'testlog': {'()': 'logging.Formatter',
            'format': "%(asctime)s %(name)s %(message)s"},
        'debug': {'()': 'colorlog.ColoredFormatter',
            'format': "%(cyan)s%(asctime)s %(name)s %(message)s"},
        'debuglog': {'()': 'logging.Formatter',
            'format': "%(asctime)s %(name)s %(message)s"},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'level': 'INFO',
            'stream': 'ext://sys.stdout',
        },
        'testlog': {
            'class': 'logging.FileHandler',
            'formatter': 'testlog',
            'level': 'INFO',
            'mode': 'wt',
            'filename': '/work/run/test.log',
        },
        'debuglog': {
            'class': 'logging.FileHandler',
            'formatter': 'debuglog',
            'level': 'INFO',
            'mode': 'wt',
            'filename': '/work/run/debug-test.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'testlog'],
            'level': 'INFO',
        },
        'kazoo': {
            'handlers': ['debuglog'],
            'level': 'INFO',
            'propagate': False,
        },
        'urllib3': {
            'handlers': ['debuglog'],
            'level': 'INFO',
            'propagate': False,
        },
    },
})
