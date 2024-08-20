# -*- coding: utf-8 -*-

import os
import dj_database_url

IS_DEPLOYED = bool(os.environ.get('is_deployed', ''))

if IS_DEPLOYED:
    DATABASE_DICT = dj_database_url.config(
        default=os.environ.get('DATABASE_URL', ''))
else:
    DATABASE_DICT = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'EVA',
        'USER': 'postgres',
        'PASSWORD': 'postgresql',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_EVA',
        }
    }
