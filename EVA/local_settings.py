# -*- coding: utf-8 -*-

import os
import dj_database_url
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

IS_DEPLOYED = bool(os.getenv("IS_DEPLOYED", ""))

if IS_DEPLOYED:
    DATABASE_DICT = dj_database_url.config(default=os.getenv("DATABASE_URL"))
else:
    DATABASE_DICT = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "EVA",
        "USER": "postgres",
        "PASSWORD": "postgresql",
        "HOST": "127.0.0.1",
        "PORT": "5432",
        "TEST": {
            "NAME": "test_EVA",
        },
    }
