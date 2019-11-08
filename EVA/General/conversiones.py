# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
from django.conf import settings


def string_to_date(fecha_string: str) -> datetime:
    """
    Convierte un string a datetime, la fecha se toma con el timezone configurado en settings.TIME_ZONE
    :param fecha_string: string con formato "%Y-%m-%d"
    :return: retorna el datetime en UTC
    """
    return datetime.strptime(fecha_string, "%Y-%m-%d").astimezone(pytz.timezone(settings.TIME_ZONE))\
        .astimezone(pytz.timezone('UTC'))
