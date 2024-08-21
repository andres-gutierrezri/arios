# -*- coding: utf-8 -*-

import os
import dj_database_url
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

IS_DEPLOYED = os.getenv('IS_DEPLOYED', 'False') == 'True'

if IS_DEPLOYED:
    DATABASE_DICT = dj_database_url.config(default=os.getenv("DATABASE_PUBLIC_URL"))
else: 
    DATABASE_DICT = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),   
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'TEST': {
            'NAME': 'test_EVA',
        },
    }
